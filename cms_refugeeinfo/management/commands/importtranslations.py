from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.core.management.base import BaseCommand
from cms.models import Page
from djangocms_text_ckeditor import cms_plugins
import tempfile
import os
import gettext
from cms import api
import xlrd
import  sys
import csv
class Command(BaseCommand):
    help = 'Import translation in excel format'

    def handle(self, *args, **options):
        if len(args) == 3:
            page_id, language, file_name = args
            reader = csv.DictReader(file_name)
            dict_list = list(reader)
        else:
            page_id, language = args
            reader = csv.DictReader(sys.stdin)
            dict_list = list(reader)
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
