# PostgreSQL: транзакции и уровни изоляции

PostgreSQL portfolio: BEGIN/COMMIT, READ COMMITTED, REPEATABLE READ, SERIALIZABLE и deadlock.

[![PostgreSQL checks](https://github.com/rootofevi1/postgresql-transactions-and-isolation/actions/workflows/sql.yml/badge.svg)](https://github.com/rootofevi1/postgresql-transactions-and-isolation/actions/workflows/sql.yml)

Учебный проект: **8 SQL-файлов** на предметной области заказов и посещений пиццерий. Часть серии из девяти проектов [SQL-портфолио](https://github.com/rootofevi1#sql-и-postgresql).

## Что реализовано

- Видимость изменений до и после COMMIT
- Конкурирующие обновления одной строки
- Повторное чтение при разных уровнях изоляции
- Изменение набора строк другой транзакцией
- Взаимная блокировка при разном порядке обновлений

## Связь с QA

Разбор конкурентных действий пользователей, воспроизведение конфликтов обновления и понимание границ транзакции.

## Стек и устройство

PostgreSQL 17 · SQL · Docker · Python 3.10+ для проверки · GitHub Actions.

- `src/` — SQL-решения, имена файлов сохранены для навигации.
- [demo/schema.sql](demo/schema.sql) и [demo/seed.sql](demo/seed.sql) — отдельная демонстрационная БД и новые синтетические данные.
- [docs/DATABASE.md](docs/DATABASE.md) — описание таблиц, ER-диаграмма и ограничения набора.
- [scripts/check.py](scripts/check.py) — запуск в изолированном временном PostgreSQL.
- [tests/assertions.sql](tests/assertions.sql) — дополнительные проверки состояния демобазы.

## Быстрый запуск

Нужны Python 3.10+ и запущенный Docker с Linux-контейнерами. Первый запуск скачивает образ `postgres:17`.

```bash
git clone https://github.com/rootofevi1/postgresql-transactions-and-isolation.git
cd postgresql-transactions-and-isolation
python3 scripts/check.py
```

В Windows PowerShell используйте `python scripts/check.py` или `py -3 scripts/check.py`.
Дополнительные Python-пакеты не требуются. Контейнер работает без сети и открытых портов,
случайный пароль передаётся только через окружение процесса. Скрипт выполняет SQL с остановкой
при ошибке и удаляет контейнер в конце. Существующие БД пользователя не затрагиваются.

Для ручного изучения создайте **новую пустую БД** на своём PostgreSQL, загрузите `demo/schema.sql`,
затем `demo/seed.sql` и выполняйте `src/*.sql` (включая вложенные папки) в порядке имён файлов.
Для каждого проекта нужна своя БД; DDL/DML не предназначены для повторного запуска поверх прежнего состояния.

Каждый транзакционный пример начинайте с новой демобазы. Для параллельного запуска откройте два сеанса и следуйте [TRANSACTIONS.md](docs/TRANSACTIONS.md).

## Навигация по решениям

| SQL-файл |
|---|
| [day08_ex00](src/ex00/day08_ex00.sql) |
| [day08_ex01](src/ex01/day08_ex01.sql) |
| [day08_ex02](src/ex02/day08_ex02.sql) |
| [day08_ex03](src/ex03/day08_ex03.sql) |
| [day08_ex04](src/ex04/day08_ex04.sql) |
| [day08_ex05](src/ex05/day08_ex05.sql) |
| [day08_ex06](src/ex06/day08_ex06.sql) |
| [day08_ex07](src/ex07/day08_ex07.sql) |

## Проверки и ограничения

GitHub Actions выполняет все 8 SQL-файлов на собственной демобазе PostgreSQL 17
и дополнительные проверки состояния/ограничений. Статус последнего запуска виден в badge выше.

Файлы src содержат команды двух сеансов вместе. Последовательное выполнение файла проверяет исполнимость, но не воспроизводит конкуренцию. Для воспроизведения нужен порядок из [сценариев](docs/TRANSACTIONS.md).

## Происхождение

Основа — мои учебные SQL-решения. Для публичного портфолио отдельно подготовлены описание,
демосхема, синтетический набор, проверки и CI. Пароли, токены, дампы реальных БД
и локальные настройки подключения не требуются.

Александр · Junior QA/AQA Engineer · [Email](mailto:a@samoylov-qa.ru) · [Telegram](https://t.me/samoylov_av)
