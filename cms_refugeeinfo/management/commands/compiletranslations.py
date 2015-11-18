from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.core.management.base import BaseCommand
from cms.models import Page
from djangocms_text_ckeditor import cms_plugins
import title_plugin.cms_plugins
import xlwt
from StringIO import StringIO

class Command(BaseCommand):
    help = 'Generate Content POT'

    def handle(self, *args, **options):
        if not args:
            return

        page_id = args[0]

        a = [a.get_public_object() for a in Page.objects.filter(id=page_id)]
        book = xlwt.Workbook()
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
                    messages.append(line)
        sheet = book.add_sheet('Translations')

        style = xlwt.XFStyle()
        aligned = xlwt.XFStyle()
        aligned.alignment.wrap = 1

        if messages:
            keys = ["text", "translated", "position", "type", "parent", "id"]
            for j, col in enumerate(keys):
                sheet.write(0, j, col)

            for i, row in enumerate(messages):
                for j, col in enumerate(keys):
                    sheet.write(i + 1, j, row[col], aligned if j < 2 else style)

        out = StringIO()
        book.save(out)

        out.seek(0)
        print(out.read())
