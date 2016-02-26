from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from cms.signals import post_publish
from django.dispatch import receiver
from . import utils
from django.conf import settings


@receiver(post_publish)
def post_publish_receiver(*args, **kwargs):
    """
    Signal receiver that is fired after publishing.

    If there is an universal setting to stop publishing to transifex it stops here
    If the translation project is managed by the IRC it also stops here.
    :param args:
    :param kwargs:
    :return:
    """
    language = kwargs.pop('language', 'en')
    page = kwargs.pop('instance', None)

    if not page:
        return

    if not settings.TRANSIFEX_UPLOAD_ON_PUBLISH:
        return

    # TODO: Refactor
    for k, v in settings.TRANSIFEX_PROJECTS.iteritems():
        if page.get_slug('en') in v:
            return

    if page and language == 'en':
        print('Pushing page {} to transifex.'.format(page.id))
        utils.push_to_transifex.delay(page.pk)
