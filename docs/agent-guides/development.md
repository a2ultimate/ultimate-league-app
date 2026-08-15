# Development

## Initial Setup

From the repository root, create the development virtual environment and install frontend dependencies:

```bash
./bin/mkvenv.sh dev
cd src/static
npm install
```

The virtual environment is created at `venv/dev/`. Recreate it from scratch with `./bin/mkvenv.sh dev clean`.

## Local Servers

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
