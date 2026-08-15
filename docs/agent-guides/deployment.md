# Production Updates

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
