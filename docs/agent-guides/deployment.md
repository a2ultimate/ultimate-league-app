# Production Updates

## Runtime Baseline

The currently deployed environment uses Ubuntu 22.04, Python 3.9.15, Node
16.18.1, npm 8.19.2, and MySQL 8.0.31. Docker development and production-like
images intentionally begin with these versions.

Runtime upgrades should update the repository pins, Docker images, dependency
requirements, and deployment host in the same pull request. Build both Docker targets,
run the Django and frontend suites, exercise MySQL migrations, and smoke-test
the production-like profile before changing the deployed host.

The production Docker target is currently a parity and migration artifact. The
host-managed virtualenv, Supervisor, Gunicorn, and Nginx deployment remains
authoritative until secrets, persistent media, rollback, and process monitoring
have been validated for a container deployment.

## Application Update

After pulling the intended revision on the production host, run:

```bash
source venv/prod/bin/activate
cd src
pip install -r requirements/prod.txt
./manage.py migrate
cd static
npm run build
cd ..
APP_RUNMODE=prod ./manage.py collectstatic
```

Before restarting the application service, compare changed settings and environment requirements with the production configuration. Restart the service using the host's service manager.
