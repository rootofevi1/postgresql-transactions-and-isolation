"""Independent concurrency checks added for the portfolio, using two real psql sessions."""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from queue import Queue, Empty
from threading import Thread
import secrets
import subprocess
import time


class Session:
    def __init__(self, container, label):
        self.lines = Queue()
        self.process = subprocess.Popen(
            ['docker','exec','-i',container,'psql','-X','-qAt','-U','postgres',
             '-d','portfolio','-v','ON_ERROR_STOP=0','-v','VERBOSITY=sqlstate'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', bufsize=1)
        self.reader = Thread(target=self._read, daemon=True)
        self.reader.start()
        self.run("SET application_name = '" + label + "';")

    def _read(self):
        for line in self.process.stdout:
            self.lines.put(line.rstrip())
        self.lines.put(None)

    def run(self, statement):
        marker = 'END_' + secrets.token_hex(8)
        self.process.stdin.write(statement + '\n\\echo ' + marker + '\n')
        self.process.stdin.flush()
        result = []
        while True:
            try:
                line = self.lines.get(timeout=20)
            except Empty:
                raise AssertionError('Timed out waiting for SQL') from None
            if line == marker:
                return result
            if line is None:
                raise AssertionError('psql exited unexpectedly: ' + repr(result))
            if line:
                result.append(line)

    def ok(self, statement):
        result = self.run(statement)
        if any('ERROR:' in line or 'FATAL:' in line for line in result):
            raise AssertionError(result)
        return result

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.write('ROLLBACK;\n\\q\n')
            self.process.stdin.flush()
            self.process.communicate(timeout=20)


def verify(container, reset):
    reset()
    a, b, observer = (Session(container, 'portfolio_' + label) for label in ('a','b','observer'))
    read = 'SELECT rating FROM pizzeria WHERE id=1;'
    update = 'UPDATE pizzeria SET rating=3.60 WHERE id=1;'

    def baseline():
        a.ok('ROLLBACK;')
        b.ok('ROLLBACK;')
        observer.ok('UPDATE pizzeria SET rating=4.15 WHERE id=1;')

    def waiting(label):
        for _ in range(80):
            rows = observer.ok("SELECT count(*) FROM pg_stat_activity WHERE application_name='portfolio_" + label + "' AND wait_event_type='Lock';")
            if rows == ['1']:
                return
            time.sleep(.05)
        raise AssertionError('Expected a blocked session')

    try:
        # Uncommitted changes are visible to the writer only.
        baseline()
        a.ok('BEGIN; ' + update)
        assert Decimal(a.ok(read)[0]) == Decimal('3.60')
        assert Decimal(b.ok(read)[0]) == Decimal('4.15')
        a.ok('COMMIT;')
        assert Decimal(b.ok(read)[0]) == Decimal('3.60')

        # Snapshot behavior: repeated row reads and a new matching row.
        for level in ('READ COMMITTED','REPEATABLE READ','SERIALIZABLE'):
            baseline()
            observer.ok('DELETE FROM pizzeria WHERE id=50;')
            a.ok('BEGIN ISOLATION LEVEL ' + level + ';')
            before = a.ok(read + ' SELECT count(*) FROM pizzeria;')
            b.ok(update + " INSERT INTO pizzeria VALUES(50,'Synthetic concurrency cafe',4.00);")
            after = a.ok(read + ' SELECT count(*) FROM pizzeria;')
            if level == 'READ COMMITTED':
                assert Decimal(after[0]) == Decimal('3.60') and int(after[1]) == int(before[1]) + 1
            else:
                assert after == before
            a.ok('COMMIT;')
        observer.ok('DELETE FROM pizzeria WHERE id=50;')

        # READ COMMITTED: a stale literal update waits, then overwrites the first value.
        baseline()
        a.ok('BEGIN; ' + read)
        b.ok('BEGIN; ' + read)
        a.ok('UPDATE pizzeria SET rating=4.00 WHERE id=1;')
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(b.ok, update)
            waiting('b')
            a.ok('COMMIT;')
            pending.result(timeout=20)
        b.ok('COMMIT;')
        assert Decimal(observer.ok(read)[0]) == Decimal('3.60')

        # REPEATABLE READ rejects an update against a changed snapshot.
        baseline()
        b.ok('BEGIN ISOLATION LEVEL REPEATABLE READ; ' + read)
        a.ok(update)
        error = b.run('UPDATE pizzeria SET rating=4.00 WHERE id=1;')
        assert any('40001' in line for line in error), error
        b.ok('ROLLBACK;')

        # Deadlock: opposite lock ordering. PostgreSQL chooses one victim.
        baseline()
        a.ok('BEGIN; UPDATE pizzeria SET rating=4.00 WHERE id=1;')
        b.ok('BEGIN; UPDATE pizzeria SET rating=4.00 WHERE id=2;')
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(a.run, 'UPDATE pizzeria SET rating=4.00 WHERE id=2;')
            waiting('a')
            second = b.run('UPDATE pizzeria SET rating=4.00 WHERE id=1;')
            first = pending.result(timeout=20)
        errors = [line for line in first + second if 'ERROR:' in line]
        assert len(errors) == 1 and '40P01' in errors[0], errors
        a.ok('ROLLBACK;')
        b.ok('ROLLBACK;')
    finally:
        a.close()
        b.close()
        observer.close()
