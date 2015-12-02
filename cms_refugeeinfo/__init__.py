from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app  # noqa
