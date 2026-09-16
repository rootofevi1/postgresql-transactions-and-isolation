"""Execute SQL in a disposable, network-isolated PostgreSQL 17 container."""
from pathlib import Path
import secrets
import subprocess
import time
import os

ROOT = Path(__file__).resolve().parent.parent
NAME = 'sql-portfolio-' + secrets.token_hex(6)

def command(*args, data=None, capture=False, check=True):
    return subprocess.run(list(args), input=data, text=True, encoding='utf-8',
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.STDOUT if capture else None, check=check)

def sql(text, capture=False):
    return command('docker','exec','-i',NAME,'psql','-X','-v','ON_ERROR_STOP=1',
                   '-U','postgres','-d','portfolio','-qAt',data=text,capture=capture)

def reset():
    # Only affects the random disposable container created by this script.
    sql('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
    sql((ROOT/'demo/schema.sql').read_text(encoding='utf-8'))
    sql((ROOT/'demo/seed.sql').read_text(encoding='utf-8'))

def main():
    env_name = 'POSTGRES_PASSWORD'
    previous = os.environ.get(env_name)
    os.environ[env_name] = secrets.token_urlsafe(32)
    try:
        command('docker','run','--detach','--rm','--name',NAME,'--network','none',
                '--env',env_name,'--env','POSTGRES_DB=portfolio',
                'postgres:17','-c','listen_addresses=','-c','statement_timeout=15000',
                '-c','idle_in_transaction_session_timeout=60000',capture=True)
        for _ in range(60):
            ready = command('docker','exec',NAME,'pg_isready','-U','postgres','-d','portfolio',
                            capture=True,check=False)
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError('PostgreSQL did not become ready')
        reset()
        files = sorted((ROOT/'src').rglob('*.sql'))
        isolation = any(p.name.startswith('day08_') for p in files)
        for path in files:
            if isolation:
                reset()
            print('RUN',path.relative_to(ROOT).as_posix(),flush=True)
            try:
                sql(path.read_text(encoding='utf-8'),capture=True)
            except subprocess.CalledProcessError as error:
                print(error.stdout, flush=True)
                raise
        sql((ROOT/'tests/assertions.sql').read_text(encoding='utf-8'),capture=True)
        if isolation:
            from isolation_check import verify
            verify(NAME, reset)
        print(f'PASS: {len(files)} SQL files executed; fixture assertions passed.')
        if isolation:
            print('PASS: independent two-session isolation checks.')
    finally:
        command('docker','rm','--force',NAME,capture=True,check=False)
        if previous is None:
            os.environ.pop(env_name,None)
        else:
            os.environ[env_name]=previous

if __name__ == '__main__':
    main()
