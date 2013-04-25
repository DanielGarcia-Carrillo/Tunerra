import os
import sys

from django.core.handlers.wsgi import WSGIHandler

sys.path.append('/home/danielgc/webapps/tunerra/myproject/myproject')
sys.path.append('/home/danielgc/webapps/tunerra/myproject')
sys.path.append('/home/danielgc/webapps/tunerra')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = WSGIHandler()
