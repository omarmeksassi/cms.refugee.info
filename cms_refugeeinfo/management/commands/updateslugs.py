from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from lxml import etree
from lxml.cssselect import CSSSelector

from django.core.management.base import BaseCommand
from cms.models import Page, Title
import StringIO
from cms import api
from django.contrib.auth import models
from django.conf import settings

class Command(BaseCommand):
    help = 'Import translation in html format'

    def handle(self, *args, **options):
        if not args:
            return

        page_id, = args

        parser = etree.HTMLParser()
        selector = CSSSelector('body')

        # content = selector(tree.getroot())
        dict_list = []

        blame = models.User.objects.filter(is_superuser=True)[0]

        main_page = Page.objects.get(id=page_id)
        sub_pages = main_page.get_descendants()
        for page in sub_pages:
            page = page.get_draft_object()
            en = page.get_title_obj('en')
            titles = Title.objects.filter(page=page).exclude(language='en')
            for title in titles:
                title.title = en.title
                title.slug = en.slug
                title.save()
                print ('Updating title of page {} language {}'.format(title.page_id, title.language))

            for l in dict(settings.LANGUAGES).keys():
                try:
                    api.publish_page(page, blame, l)
                except Exception as e:
                    pass