from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'


from cms.signals import post_publish
from django.dispatch import receiver
from . import utils

@receiver(post_publish)
def post_publish_receiver(*args, **kwargs):
    language = kwargs.pop('language', 'en')
    page = kwargs.pop('instance', None)
    if page and language == 'en':
        print('Pushing page {} to Jira.'.format(page.id))
        utils.upsert_jira_ticket.delay(page.pk)
