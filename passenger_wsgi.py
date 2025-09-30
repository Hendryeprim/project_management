import sys
import os

# Project root path
sys.path.insert(0, '/opt/render/project/src')  

# Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

# WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
