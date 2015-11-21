from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import render
from cms.models import Title
import email.utils
import time

import requests
import json
from cms.utils import copy_plugins
import cms.api

from lxml import etree
from lxml.cssselect import CSSSelector
from StringIO import StringIO


SHIM_LANGUAGE_DICTIONARY = {
    'af': 'ps'
}
"""
The Shim above is because django doesnt support Pashto, but Transifex does.
"""


def generate_blank(request, slug):
    staging = Title.objects.filter(language='en', slug='staging')
    if staging:
        staging = staging[0].page
    titles = Title.objects.filter(language='en', slug=slug, page__in=staging.get_descendants())

    if not titles:
        raise Http404

    page = titles[0].page.get_public_object()

    html = _generate_html_for_translations(titles[0], page)

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
    html = _generate_html_for_translations(titles[0], page)

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
        r2 = requests.put(fetch_format.format(**transifex_url_data) + 'content/',
                          headers={"Content-type": "application/json"},
                          auth=(user, password),
                          data=json.dumps(payload), )
        print('Updated', r2.text)

    return render(request, "push-to-transifex.html", {}, context_instance=RequestContext(request))


def pull_from_transifex(request, slug, language):
    staging = Title.objects.filter(language=language, slug='staging')
    if staging:
        staging = staging[0].page
    titles = Title.objects.filter(language=language, slug=slug, page__in=staging.get_descendants())

    if not titles:
        raise Http404

    page = titles[0].page.get_draft_object()

    password = settings.TRANSIFEX_PASSWORD
    user = settings.TRANSIFEX_USER

    transifex_language = language
    if language in SHIM_LANGUAGE_DICTIONARY.keys():
        transifex_language = SHIM_LANGUAGE_DICTIONARY[language]

    transifex_url_data = {
        "project": settings.TRANSIFEX_PROJECT_SLUG,
        "slug": page.get_slug('en'),
        "language": transifex_language
    }
    fetch_format = "http://www.transifex.com/api/2/project/{project}/resource/{slug}html/translation/{language}/?mode=default"

    r = requests.get(fetch_format.format(**transifex_url_data), auth=(user, password))

    translation = r.json()
    html = StringIO(translation['content'])

    parser = etree.HTMLParser()
    tree = etree.parse(html, parser)
    selector = CSSSelector('div[data-id]')
    title_selector = CSSSelector('div.title')

    """
    Directions are handled application-wise
    """
    p_selector = CSSSelector('p[dir]')

    for p in p_selector(tree.getroot()):
        del p.attrib['dir']

    content = selector(tree.getroot())
    title = title_selector(tree.getroot())
    if title:
        title = title[0].text
        title_obj = page.get_title_obj(language)
        title_obj.page_title = title
        title_obj.save()

    dict_list = []

    for div in content:
        plugin_dict = {
            'id': div.attrib['data-id'],
            'type': div.attrib['data-type'],
            'parent': div.attrib['data-parent'],
            'position': div.attrib['data-position'],
            'translated': (div.text or '') + ''.join([
                etree.tostring(a, pretty_print=True, method="html") for a in div
            ]),
        }
        dict_list.append(plugin_dict)

    _translate_page(dict_list, language, page)
    cms.api.publish_page(page, request.user, language)

    return render(request, "promote-to-production.html", {}, context_instance=RequestContext(request))


def copy_from_production(request, slug):
    staging = Title.objects.filter(language='en', slug='staging')
    production = Title.objects.filter(language='en', slug='production')
    if staging:
        staging = staging[0].page
    if production:
        production = production[0].page
    staging_title = Title.objects.filter(language='en', slug=slug, page__in=staging.get_descendants())
    production_title = Title.objects.filter(language='en', slug=slug, page__in=production.get_descendants())

    if staging_title and production_title:
        staging_title = staging_title[0]
        production_title = production_title[0]

        staging_page = staging_title.page
        production_page = production_title.page

        _duplicate_page(production_page, staging_page, True, request.user)

    return render(request, "copy-from-production.html", {}, context_instance=RequestContext(request))


def promote_to_production(request, slug):
    staging = Title.objects.filter(language='en', slug='staging')
    production = Title.objects.filter(language='en', slug='production')
    if staging:
        staging = staging[0].page
    if production:
        production = production[0].page
    staging_title = Title.objects.filter(language='en', slug=slug, page__in=staging.get_descendants())
    production_title = Title.objects.filter(language='en', slug=slug, page__in=production.get_descendants())

    if staging_title and production_title:
        staging_title = staging_title[0]
        production_title = production_title[0]

        staging_page = staging_title.page
        production_page = production_title.page

        _duplicate_page(staging_page, production_page, False, request.user)

    return render(request, "promote-to-production.html", {}, context_instance=RequestContext(request))


def _duplicate_page(source, destination, publish=None, user=None):
    placeholders = source.get_placeholders()

    source = source.get_public_object()
    destination = destination.get_draft_object()

    destination_placeholders = dict([(a.slot, a) for a in destination.get_placeholders()])
    for k, v in settings.LANGUAGES:
        available = [a.language for a in destination.title_set.all()]
        title = source.get_title_obj(language=k)
        if not k in available:
            cms.api.create_title(k, title.title, destination, menu_title=title.menu_title, slug=title.slug)

    for placeholder in placeholders:
        destination_placeholders[placeholder.slot].clear()

        for k, v in settings.LANGUAGES:
            plugins = list(
                placeholder.cmsplugin_set.filter(language=k).order_by('path')
            )
            copied_plugins = copy_plugins.copy_plugins_to(plugins, destination_placeholders[placeholder.slot], k)
    if publish:
        try:
            for k, v in settings.LANGUAGES:
                cms.api.publish_page(destination, user, k)
        except Exception as e:
            pass


def _generate_html_for_translations(title, page):
    messages = []
    for placeholder in page.get_placeholders():
        sort_function = lambda item: item.get_plugin_instance()[0].get_position_in_placeholder()
        plugins = sorted(placeholder.get_plugins('en'), key=sort_function)

        for plugin in plugins:
            line = {}
            instance, t = plugin.get_plugin_instance()
            line.update(id=instance.id)
            line.update(position=instance.get_position_in_placeholder())

            type_name = type(t).__name__
            line.update(type=type_name)

            if instance.get_parent():
                line.update(parent=instance.get_parent().id)
            else:
                line.update(parent='')

            if hasattr(instance, 'body'):
                line.update(text=instance.body.encode('ascii', 'xmlcharrefreplace'))
            elif hasattr(instance, 'title'):
                line.update(text=instance.title.encode('ascii', 'xmlcharrefreplace'))
            elif hasattr(instance, 'name'):
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
    html += "<div class='title'>{}</div>".format(title.page_title)
    html += '\n'.join(
        [div_format.format(**a) for a in messages]
    )
    html += "</body>"
    html += "</html>"

    return html


def _translate_page(dict_list, language, page):
    for c in page.get_placeholders():
        c.clear(language)
    cms.api.copy_plugins_to_language(page, 'en', language)
    for c in page.get_placeholders():
        for d in c.get_plugins(language):
            instance, t = d.get_plugin_instance()
            type_name = type(t).__name__
            position = instance.get_position_in_placeholder()
            translation = [a for a in dict_list if int(a['position']) == position and a['type'] == type_name]

            if translation:
                translation = translation[0]
                translation['translated_id'] = instance.id

                text = translation['translated']

                if hasattr(instance, 'body'):
                    instance.body = text
                elif hasattr(instance, 'title'):
                    instance.title = text
                elif hasattr(instance, 'name'):
                    instance.name = text
                instance.save()