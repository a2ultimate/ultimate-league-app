# Development

## Docker Setup

The primary development environment uses Docker Compose and matches the
currently deployed Python 3.9.15, Node 16.18.1, npm 8.19.2, and MySQL 8.0.31
versions.

Install Docker Desktop with Docker Compose v2, then run from the repository
root:

```bash
docker compose up --build
```

The Django application is available at <http://localhost:8000>. Webpack dev
server assets and hot module replacement use <http://localhost:8080>.

Source files are bind-mounted. Django reloads after Python and template edits,
and webpack hot-reloads JavaScript and SCSS edits. MySQL and uploaded media use
named volumes and survive container recreation.

Common commands are available through the Makefile:

```bash
make up
make logs
make shell
make test
make check
make down
```

The equivalent raw Compose commands remain available. For example:

```bash
docker compose logs --follow backend frontend db
docker compose exec backend python manage.py shell
```

### Import a Database Dump

Import a plain or gzip-compressed MySQL dump with:

```bash
make db-import FILE=/path/to/production.sql.gz
# or
./bin/import-db.sh /path/to/production.sql
```

The script confirms before replacing the Compose-managed local database and
stops both application backends before import. It restarts whichever backends
were running, or starts the development backend if neither was running, so
migrations run before the application serves requests. If stopping a backend
fails, the database is left untouched. Pass `--yes` directly to
`bin/import-db.sh` for an explicit non-interactive import.

Production dumps contain sensitive user and session data. Keep them outside
this repository and do not add them to Docker images. A database dump may also
reference uploaded media that is not present locally.

### Reset Local Data

`make clean` removes all Compose volumes after confirmation, including the
local database, uploaded media, and installed frontend dependencies.

### Production-Like Mode

The optional production-like profile builds immutable frontend assets, runs
Django with production settings under Gunicorn, collects static files, and
serves the application through Nginx:

```bash
make prodlike
```

It is available at <http://localhost:8081>. This mode is for parity checks; use
the default development environment for normal editing and hot reload.

## Native Setup

From the repository root, create the development virtual environment and install frontend dependencies:

```bash
./bin/mkvenv.sh dev
cd src/static
npm install
```

The virtual environment is created at `venv/dev/`. Recreate it from scratch with `./bin/mkvenv.sh dev clean`.

## Native Local Servers

Run the Django and webpack development servers in separate terminals.

From the repository root, start Django:

```bash
source venv/dev/bin/activate
cd src
./manage.py runserver_plus
```

From the repository root, start webpack:

```bash
cd src/static
npm run dev
```
