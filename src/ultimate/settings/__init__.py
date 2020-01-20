import logging
import os

app_runmode = os.environ.get('APP_RUNMODE', None)

if app_runmode == 'dev':
    logging.info('Loading DEVELOPMENT environment...')
    from .dev import *
elif app_runmode == 'prod':
    logging.info('Loading PRODUCTION environment...')
    from .prod import *
else:
    logging.info('Invalid value for APP_RUNMODE `{}`, loading DEVELOPMENT environment...:'.format(app_runmode))
    from .dev import *
