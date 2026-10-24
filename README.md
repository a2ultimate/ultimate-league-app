# ultimate-league-app

Ultimate Frisbee League Web Application

## Run the Development Environment

Install Docker Desktop with Docker Compose v2, then run from the repository root:

```bash
docker compose up --build
```

The application is available at <http://localhost:8000>. Backend and frontend
source changes reload automatically. See
[the development guide](docs/agent-guides/development.md) for database imports,
tests, logs, production-like mode, and the native setup alternative.

```bash
make up
make test
make logs
```

## Update a Production Environment

Once you are deployed in production, you can pull new code and update with the following:

```bash
git pull
source venv/prod/bin/activate
cd src/
pip install -r requirements/prod.txt
./manage.py migrate
cd static/
npm run build
cd ..
APP_RUNMODE=prod ./manage.py collectstatic
```

_Do not forget to check for settings changes!_

Then, you will want to restart your server service.
