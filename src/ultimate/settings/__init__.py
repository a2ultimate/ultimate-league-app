import logging
import os

ultimate_runmode = os.environ.get('ULTIMATE_RUNMODE', None)

if ultimate_runmode == 'dev':
    logging.info('Loading DEVELOPMENT environment...')
    from .dev import *
elif ultimate_runmode == 'prod':
    logging.info('Loading PRODUCTION environment...')
    from .prod import *
else:
    logging.info('Invalid value for ULTIMATE_RUNMODE `{}`, loading DEVELOPMENT environment...:'.format(ultimate_runmode))
    from .dev import *
