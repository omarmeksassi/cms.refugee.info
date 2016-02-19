from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from cms.signals import post_publish
from django.dispatch import receiver
from . import utils
from django.conf import settings


@receiver(post_publish)
def post_publish_receiver(*args, **kwargs):
    if not settings.TRANSIFEX_UPLOAD_ON_PUBLISH:
        return

    language = kwargs.pop('language', 'en')
    page = kwargs.pop('instance', None)
    if page and language == 'en':
        print('Pushing page {} to transifex.'.format(page.id))
        utils.push_to_transifex.delay(page.pk)
