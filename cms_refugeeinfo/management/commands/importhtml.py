from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.conf import settings

from lxml import etree
from StringIO import StringIO
from lxml.cssselect import CSSSelector

from django.core.management.base import BaseCommand
from cms.models import Page
from djangocms_text_ckeditor import cms_plugins
import tempfile
import os
import gettext
from cms import api
import  sys
import csv
class Command(BaseCommand):
    help = 'Import translation in html format'

    def handle(self, *args, **options):

        if len(args) == 3:
            page_id, language, file_name = args
            with open(file_name, 'r') as f:
                html = StringIO(f.read().decode('utf-8').encode('ascii', 'xmlcharrefreplace'))
        else:
            page_id, language = args
            html = StringIO(sys.stdin.read().decode('utf-8').encode('ascii', 'xmlcharrefreplace'))

        parser = etree.HTMLParser()
        tree = etree.parse(html, parser)
        selector = CSSSelector('div[data-id]')

        content = selector(tree.getroot())
        dict_list = [        ]

        for div in content:
            plugin_dict = {}
            plugin_dict['id'] = div.attrib['data-id']
            plugin_dict['type'] = div.attrib['data-type']
            plugin_dict['parent'] = div.attrib['data-parent']
            plugin_dict['position'] = div.attrib['data-position']
            plugin_dict['translated'] = (div.text or '') + ''.join([
                etree.tostring(a, pretty_print=True, method="html") for a in div
            ])
            dict_list.append(plugin_dict)

        a = [a for a in Page.objects.filter(id=page_id)]
        for b in a:
            print('Clearing Placeholders')
            for c in b.get_placeholders():
                c.clear(language)
            print('Copying Plugins')
            api.copy_plugins_to_language(b, 'en', language)
            for c in b.get_placeholders():
                for d in c.get_plugins(language):
                    instance, t = d.get_plugin_instance()
                    typename = type(t).__name__
                    position = instance.get_position_in_placeholder()
                    translation = [a for a in dict_list if int(a['position']) == position and a['type'] == typename]
                    if translation:
                        translation = translation[0]
                        translation['translated_id'] = instance.id
                        if typename == "TextPlugin":
                            instance.body = translation['translated']
                        elif typename == "CMSTitlePlugin":
                            instance.title = translation['translated']
                        elif typename == "CMSLinkButtonPlugin":
                            instance.name = translation['translated']
                        print('Translated', typename)
                        instance.save()
