from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from lxml import etree
from lxml.cssselect import CSSSelector

from django.core.management.base import BaseCommand
from cms.models import Page
import StringIO


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

        page = Page.objects.get(id=page_id)
        page = page.get_draft_object()
        for placeholder in page.get_placeholders():
            for plugin in placeholder.get_plugins('en'):
                instance, t = plugin.get_plugin_instance()
                typename = type(t).__name__
                if typename == 'TextPlugin':
                    tree = etree.parse(StringIO.StringIO(instance.body), parser).getroot()
                    for child in instance.get_children():
                        child_instance, child_type = child.get_plugin_instance()
                        child_type_name = type(child_type).__name__

                        img = CSSSelector('[id=plugin_obj_{}]'.format(child_instance.id))(tree)
                        if not img:
                            continue

                        img = img[0]
                        parent = img.getparent()
                        element = None

                        if child_type_name == "LinkPlugin":
                            element = etree.Element('a', attrib={
                                "target": "_blank",
                                "href": child_instance.url
                            })
                            element.text = child_instance.name
                        elif child_type_name == "CMSLinkButtonPlugin":
                            element = etree.Element('a', attrib={
                                "class": "link-button",
                                "target": "_blank",
                                "href": child_instance.url
                            })
                            element.text = child_instance.name

                        if element is not None:
                            parent.insert(parent.index(img), element)
                            parent.remove(img)

                            child.delete()

                    body = selector(tree)[0]

                    out = (body.text or '') + '\n'.join(
                        [etree.tostring(h, pretty_print=True, method="html") for h in list(body)]
                    )

                    instance.body = out
                    instance.save()
