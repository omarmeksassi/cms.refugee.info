from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.conf import settings
from cms.models import Title, Page
import json
from django.core.cache import cache

from cms_refugeeinfo import celery_app
import time

from lxml import etree
from lxml.cssselect import CSSSelector

import requests
from StringIO import StringIO
from collections import OrderedDict
import re

@celery_app.task
def push_to_transifex(page_pk):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    page = Page.objects.get(pk=page_pk)
    staging = Title.objects.filter(language='en', slug='staging')
    if staging:
        staging = staging[0].page
    if page in staging.get_descendants():
        page = page.get_public_object()
        html = _generate_html_for_translations(page.get_title_obj(language='en'), page)

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


SHIM_LANGUAGE_DICTIONARY = {
    'ps': 'af'
}
"""
The Shim above is because django doesnt support Pashto, but Transifex does.
"""


@celery_app.task
def pull_from_transifex(slug, language, retry=True):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        if language == 'en':
            return
        import cms.api

        internal_language = language if language not in SHIM_LANGUAGE_DICTIONARY else SHIM_LANGUAGE_DICTIONARY[language]

        # cache.add fails if the key already exists
        acquire_lock = lambda: cache.add('publishing-translation', 'true', 60 * 5)
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        release_lock = lambda: cache.delete('publishing-translation')

        while True:
            if acquire_lock():
                break
            time.sleep(5)

        staging = Title.objects.filter(language='en', slug='staging')
        if staging:
            staging = staging[0].page
        titles = Title.objects.filter(language='en', slug=slug, page__in=staging.get_descendants())

        if not titles:
            print('Page not found. Ignoring.')
            return

        page = titles[0].page.get_draft_object()

        password = settings.TRANSIFEX_PASSWORD
        user = settings.TRANSIFEX_USER

        transifex_language = language
        transifex_url_data = {
            "project": settings.TRANSIFEX_PROJECT_SLUG,
            "slug": page.get_slug('en'),
            "language": transifex_language
        }
        fetch_format = "http://www.transifex.com/api/2/project/{project}/resource/{slug}html/translation/{language}/?mode=default"

        print("Trying to request:", fetch_format.format(**transifex_url_data))
        print("With creds:", user, password)

        r = requests.get(fetch_format.format(**transifex_url_data), auth=(user, password))

        print("Received from transifex:", r.text)
        translation = r.json()
        html = StringIO(translation['content'])

        parser = etree.HTMLParser()
        tree = etree.parse(html, parser)
        selector = CSSSelector('div[data-id]')
        title_selector = CSSSelector('div.title')

        """
        Directions are handled application-wise
        """
        dir_selector = CSSSelector('[dir]')

        for element in dir_selector(tree.getroot()):
            del element.attrib['dir']

        content = selector(tree.getroot())
        title = title_selector(tree.getroot())
        if title:
            try:
                title = title[0].text
                title_obj = page.get_title_obj(internal_language, fallback=False)
                if type(title_obj).__name__ == 'EmptyTitle':
                    print('Creating new title')
                    en_title_obj = page.get_title_obj('en')
                    title_obj = cms.api.create_title(
                        language=internal_language,
                        title=en_title_obj.title,
                        page=page,
                        slug=en_title_obj.slug,
                    )
                    title_obj.save()
                title_obj.page_title = title
                title_obj.save()
            except Exception as e:
                print('Error updating the application.')

        dict_list = []

        for div in content:
            plugin_dict = {
                'id': div.attrib['data-id'],
                'type': div.attrib['data-type'],
                'parent': div.attrib['data-parent'],
                'position': div.attrib['data-position'],
                'translated': (div.text or '') + u''.join([
                    etree.tostring(a, pretty_print=True, method="html") for a in div
                ]),
            }
            dict_list.append(plugin_dict)
        blame = User.objects.filter(is_staff=True)[0]

        _translate_page(dict_list, internal_language, page)
        cms.api.publish_page(page, blame, internal_language)
        release_lock()
    except Exception as e:
        if retry:
            time.sleep(5)
            pull_from_transifex.delay(slug, language, False)
        else:
            print('Tried to retry it but it still erred out.')
            raise e


@celery_app.task
def promote_page(slug, publish=None, user_id=None, languages=None):
    import cms.api
    from cms.utils import copy_plugins
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if not user_id:
        user = User.objects.filter(is_staff=True)[0]
    else:
        user = User.objects.get(pk=user_id)

    staging = Title.objects.filter(language='en', slug='staging')
    production = Title.objects.filter(language='en', slug='production')

    if staging:
        staging = staging[0].page
    if production:
        production = production[0].page

    staging_title = Title.objects.filter(language='en', slug=slug, page__in=staging.get_descendants())
    production_title = Title.objects.filter(language='en', slug=slug, page__in=production.get_descendants())

    try:
        if staging_title and not production_title:
            staging_page = staging_title[0].page
            parent_slug = staging_page.parent.get_slug('en')
            production_parent_title = Title.objects.filter(language='en',
                                                           slug=parent_slug,
                                                           page__in=production.get_descendants())

            if production_parent_title:
                production_parent_title = production_parent_title[0]

                cms.api.create_page(**{
                    "title": staging_title[0].title,
                    "template": staging_page.template,
                    "language": 'en',
                    "menu_title": staging_title[0].menu_title,
                    "slug": staging_title[0].slug,
                    "created_by": user,
                    "parent": production_parent_title.page,
                    "in_navigation": True
                })

                production_title = Title.objects.filter(language='en', slug=slug, page__in=production.get_descendants())
    except:
        print ("Error creating production page.")

    if staging_title and production_title:
        staging_title = staging_title[0]
        production_title = production_title[0]

        source = staging_title.page
        destination = production_title.page

        placeholders = source.get_placeholders()

        source = source.get_public_object()
        destination = destination.get_draft_object()
        en_title = source.get_title_obj(language='en')

        destination_placeholders = dict([(a.slot, a) for a in destination.get_placeholders()])
        languages = languages or [k for k, v in settings.LANGUAGES]

        for k in languages:
            available = [a.language for a in destination.title_set.all()]
            title = source.get_title_obj(language=k)

            # Doing some cleanup while I am at it
            if en_title and title:
                title.title = en_title.title
                title.slug = en_title.slug
                if hasattr(title, 'save'):
                    title.save()

            if not k in available:
                cms.api.create_title(k, title.title, destination, slug=title.slug)

            try:
                destination_title = destination.get_title_obj(language=k)
                if en_title and title and destination_title:
                    destination_title.page_title = title.page_title
                    destination_title.slug = en_title.slug

                    if hasattr(destination_title, 'save'):
                        destination_title.save()

            except Exception as e:
                print("Error updating title.")

        for placeholder in placeholders:
            destination_placeholders[placeholder.slot].clear()

            for k in languages:
                plugins = list(
                    placeholder.cmsplugin_set.filter(language=k).order_by('path')
                )
                copied_plugins = copy_plugins.copy_plugins_to(plugins, destination_placeholders[placeholder.slot], k)
        if publish:
            try:
                for k in languages:
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

            if line['text']:
                line['text'] = _order_attributes(line['text'])

            messages.append(line)
    div_format = """<div data-id="{id}"
    data-position="{position}"
    data-type="{type}"
    data-parent="{parent}">{text}</div>"""
    html = "<html>"
    html += "<body>"
    html += "<div class='title'>{}</div>".format(title.page_title or title.title)
    html += '\n'.join(
        [div_format.format(**a) for a in messages]
    )
    html += "</body>"
    html += "</html>"

    return html


def _translate_page(dict_list, language, page):
    import cms.api

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
                    if type_name == "CMSTitlePlugin":
                        import HTMLParser

                        p = HTMLParser.HTMLParser()

                        instance.title = p.unescape(strip_html(text)).strip()
                    else:
                        instance.title = text
                elif hasattr(instance, 'name'):
                    instance.name = text
                instance.save()


def _order_attributes(text):
    root = "<body>{}</body>".format(text)

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(text), parser)

    body = tree.getroot()
    return_list = []

    for e in body.iterdescendants():
        if e == body:
            continue
        _copy = OrderedDict(e.attrib)
        for k in e.attrib.keys():
            del e.attrib[k]
        for k in sorted(_copy.keys()):
            e.attrib[k] = _copy[k]

    for e in list(body.iterchildren())[0]:
        element_text = etree.tostring(e, pretty_print=True, method="html")
        return_list.append(element_text)

    return "\n".join(return_list)


def strip_html(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)