from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.http import HttpResponse, Http404
from django.conf import settings
from cms.models import Title
import djangocms_text_ckeditor.cms_plugins
import title_plugin.cms_plugins
import email.utils
import time

import requests
import json


def generate_blank(request, slug):
    staging = Title.objects.filter(language='en', slug='staging')
    if staging:
        staging = staging[0].page
    titles = Title.objects.filter(language='en', slug=slug, page__in=staging.get_descendants())

    if not titles:
        raise Http404

    page = titles[0].page.get_public_object()

    messages = []
    for placeholder in page.get_placeholders():
        for plugin in placeholder.get_plugins('en'):
            line = {}
            instance, t = plugin.get_plugin_instance()
            line.update(id=instance.id)
            line.update(position=instance.get_position_in_placeholder())
            line.update(type=type(t).__name__)
            if instance.get_parent():
                line.update(parent=instance.get_parent().id)
            else:
                line.update(parent='')

            if type(t) is djangocms_text_ckeditor.cms_plugins.TextPlugin:
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

    div_format = """<div data-id="{id}"
    data-position="{position}"
    data-type="{type}"
    data-parent="{parent}">{text}</div>"""

    html = "<html>"
    html += "<body>"
    html += '\n'.join(
        [div_format.format(**a) for a in messages]
    )
    html += "</body>"
    html += "</html>"

    timestamp = time.mktime(page.publication_date.timetuple())

    response = HttpResponse(html, content_type="text/html")
    response['Last-Modified'] = email.utils.formatdate(timestamp)
    return response


def push_to_transifex(request, slug):
    staging = Title.objects.filter(language='en', slug='staging')
    if staging:
        staging = staging[0].page
    titles = Title.objects.filter(language='en', slug=slug, page__in=staging.get_descendants())

    if not titles:
        raise Http404

    page = titles[0].page.get_public_object()

    messages = []
    for placeholder in page.get_placeholders():
        for plugin in placeholder.get_plugins('en'):
            line = {}
            instance, t = plugin.get_plugin_instance()
            line.update(id=instance.id)
            line.update(position=instance.get_position_in_placeholder())
            line.update(type=type(t).__name__)
            if instance.get_parent():
                line.update(parent=instance.get_parent().id)
            else:
                line.update(parent='')

            if type(t) is djangocms_text_ckeditor.cms_plugins.TextPlugin:
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

    div_format = """<div data-id="{id}"
    data-position="{position}"
    data-type="{type}"
    data-parent="{parent}">{text}</div>"""

    html = "<html>"
    html += "<body>"
    html += '\n'.join(
        [div_format.format(**a) for a in messages]
    )
    html += "</body>"
    html += "</html>"

    timestamp = time.mktime(page.publication_date.timetuple())

    password = settings.TRANSIFEX_PASSWORD
    user = settings.TRANSIFEX_USER

    transifex_url_data = {
        "project": settings.TRANSIFEX_PROJECT_SLUG,
        "slug": page.get_slug('en')
    }
    fetch_format = "http://www.transifex.com/api/2/project/{project}/resource/{slug}html/"
    post_format = "http://www.transifex.com/api/2/project/{project}/resources/"

    r = requests.get(fetch_format.format(**transifex_url_data), auth=(user, password))

    is_new = r.status_code == 404

    payload = {
        "content": html,
        "slug": transifex_url_data['slug'] + 'html',
        "name": transifex_url_data['slug'] + '.html',
    }
    if is_new:
        payload.update({
            "i18n_type": 'HTML',
        })
        r2 = requests.post(post_format.format(**transifex_url_data),
                           headers={"Content-type": "application/json"},
                           auth=(user, password),
                           data=json.dumps(payload), )
        print('New', r2.text)
    else:
        r2 = requests.put(fetch_format.format(**transifex_url_data),
                          headers={"Content-type": "application/json"},
                          auth=(user, password),
                          data=json.dumps(payload), )
        print('Updated', r2.text)

    return HttpResponse()


def upload_translations(request, slug):
    raise Http404