import os
import sys

# Project root path (cPanel full path கொடுக்கணும்)
sys.path.insert(0, '/home/prasowla/project.prasowlabs.in')

# Django settings path
os.environ['DJANGO_SETTINGS_MODULE'] = 'projectmanager.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
