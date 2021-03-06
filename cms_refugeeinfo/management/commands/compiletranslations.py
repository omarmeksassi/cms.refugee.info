from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.core.management.base import BaseCommand
from cms.models import Page
from djangocms_text_ckeditor import cms_plugins
import title_plugin.cms_plugins
import xlwt
from StringIO import StringIO
import csv

class Command(BaseCommand):
    help = 'Generate Content POT'

    def handle(self, *args, **options):
        if not args:
            return

        page_id = args[0]
        is_html = True if len(args) == 1 else False if args[1] == 'csv' else True

        a = [a.get_public_object() for a in Page.objects.filter(id=page_id)]
        messages = []
        for b in a:
            for c in b.get_placeholders():
                for d in c.get_plugins('en'):
                    line = {}
                    instance, t = d.get_plugin_instance()
                    line.update(id=instance.id)
                    line.update(position=instance.get_position_in_placeholder())
                    line.update(type=type(t).__name__)
                    if instance.get_parent():
                        line.update(parent=instance.get_parent().id)
                    else:
                        line.update(parent='')

                    if type(t) is cms_plugins.TextPlugin:
                        line.update(text=instance.body.encode('ascii', 'xmlcharrefreplace'))
                    elif type(t) is title_plugin.cms_plugins.CMSTitlePlugin:
                        line.update(text=instance.title.encode('ascii', 'xmlcharrefreplace'))
                    elif type(t) is title_plugin.cms_plugins.CMSLinkButtonPlugin:
                        line.update(text=instance.name.encode('ascii', 'xmlcharrefreplace'))
                    else:
                        line.update(text='')
                    line.update(translated='')
                    line['text'] = line['text'].replace('&#160;', ' ')
                    messages.append(line)

        out = StringIO()
        keys = ["text", "translated", "position", "type", "parent", "id"]

        writer = csv.DictWriter(out, keys, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(messages)

        div_format = """<div data-id="{id}"
        data-position="{position}"
        data-type="{type}"
        data-parent="{parent}">{text}</div>"""
        out.seek(0)

        html = "<html>"
        html += "<body>"
        html += '\n'.join(
            [div_format.format(**a) for a in messages]
        )
        html += "</body>"
        html += "</html>"

        if not is_html:
            print(out.read())
        else:
            print (html)
