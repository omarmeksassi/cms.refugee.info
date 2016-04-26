from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms_refugeeinfo.settings')

from django.conf import settings  # noqa

app = Celery('cms')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    BROKER_URL='django://',
    CELERYD_HIJACK_ROOT_LOGGER=False
)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
