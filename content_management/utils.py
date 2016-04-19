from __future__ import absolute_import, unicode_literals, division, print_function

import json
import re
import time
from StringIO import StringIO
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup
from cms.models import Title, Page
from django.conf import settings
from django.core.cache import cache
from lxml import etree
from lxml.cssselect import CSSSelector
from six.moves import html_parser

from cms_refugeeinfo import celery_app

SHIM_LANGUAGE_DICTIONARY = {
    'ps': 'af'
}
"""
The Shim above is because django doesnt support Pashto, but Transifex does.
"""


@celery_app.task
def push_to_transifex(page_pk):
    try:
        from django.contrib.auth import get_user_model

        User = get_user_model()

        page = Page.objects.get(pk=page_pk)
        staging = Title.objects.filter(language='en', slug='staging')
        if staging:
            staging = staging[0].page
        if page in staging.get_descendants():
            page = page.get_public_object()
            html = generate_html_for_translations(page.get_title_obj(language='en'), page)

            password = settings.TRANSIFEX_PASSWORD
            user = settings.TRANSIFEX_USER

            project = settings.TRANSIFEX_PROJECT_SLUG

            # TODO: Refactor
            for k, v in settings.TRANSIFEX_PROJECTS.iteritems():
                if page.get_slug('en') in v:
                    project = k

            transifex_url_data = {
                "project": project,
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

            pull_completed_from_transifex.delay(page_pk)
    except Exception as e:
        print(e)


@celery_app.task
def pull_completed_from_transifex(page_pk):
    import time

    # Transifex just received the new file. Lets wait a few seconds before asking it to give us the translations.
    time.sleep(30)

    try:
        page = Page.objects.get(pk=page_pk)

        slug = page.get_slug('en')

        password = settings.TRANSIFEX_PASSWORD
        user = settings.TRANSIFEX_USER

        project = settings.TRANSIFEX_PROJECT_SLUG

        # TODO: Refactor
        for k, v in settings.TRANSIFEX_PROJECTS.iteritems():
            if page.get_slug('en') in v:
                project = k

        transifex_url_data = {
            "project": project,
            "slug": slug,
        }
        fetch_format = "http://www.transifex.com/api/2/project/{project}/resource/{slug}html/stats/"

        print("Trying to request:", fetch_format.format(**transifex_url_data))
        print("With creds:", user, password)

        r = requests.get(fetch_format.format(**transifex_url_data), auth=(user, password))

        # print("Received from transifex:", r.text)
        trans = r.json()

        for language in trans.keys():
            if trans[language]['completed'] == "100%":
                pull_from_transifex(slug, language, project)

        from project_management import utils as project

        project.transition_jira_ticket(slug)
    except Exception as e:
        print('')


@celery_app.task
def pull_from_transifex(slug, language, project=settings.TRANSIFEX_PROJECT_SLUG, retry=True):
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
            "project": project,
            "slug": page.get_slug('en'),
            "language": transifex_language
        }
        fetch_format = "http://www.transifex.com/api/2/project/{project}/resource/{slug}html/translation/{language}/?mode=default"

        print("Trying to request:", fetch_format.format(**transifex_url_data))
        print("With creds:", user, password)

        r = requests.get(fetch_format.format(**transifex_url_data), auth=(user, password))

        translation = r.json()

        text = translation['content'].strip()
        text = _parse_html_for_content(text)

        html = StringIO(text)

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
                                                              etree.tostring(a, pretty_print=True, method="html") for a
                                                              in div
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
            pull_from_transifex.delay(slug, language, project, False)
        else:
            print('Tried to retry it but it still erred out.')
            raise e


@celery_app.task
def promote_page(slug, publish=None, user_id=None, languages=None):
    import cms.api
    from cms.utils import copy_plugins
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:

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

                    production_title = Title.objects.filter(language='en', slug=slug,
                                                            page__in=production.get_descendants())
        except:
            print("Error creating production page.")

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
                        destination_title.title = title.title
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
                    copied_plugins = copy_plugins.copy_plugins_to(plugins, destination_placeholders[placeholder.slot],
                                                                  k)

            for k in languages:
                source_title = source.get_title_obj(language=k)
                destination_title = destination.get_title_obj(language=k)

                source_html = generate_html_for_diff(title=source_title, language=k)
                destination_html = generate_html_for_diff(title=destination_title, language=k)

                import difflib

                diff_generator = difflib.context_diff(source_html.splitlines(True),
                                                      destination_html.splitlines(True))
                diff = ''.join(list(diff_generator))

                if diff:
                    print("There is an inconsistency between staging and production. Language {}".format(k))
                    print("".join(diff))

                    raise Exception("Incorrect Diff")

            if publish:
                try:
                    for k in languages:
                        cms.api.publish_page(destination, user, k)
                except Exception as e:
                    print(e)
                    pass
    except Exception as e:
        print(e)
        time.sleep(10)
        promote_page.delay(slug=slug, publish=publish, user_id=user_id, languages=languages)


def generate_html_for_diff(page=None, title=None, language='en'):
    if not page and title:
        page = title.page
    else:
        return ""

    messages = []
    for placeholder in page.get_placeholders():
        sort_function = lambda item: item.get_plugin_instance()[0].get_position_in_placeholder()
        plugins = sorted(placeholder.get_plugins(language), key=sort_function)

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

    div_format = """<div>{text}</div>"""
    html = "<html>"
    html += "<body>"
    html += "<div class='title'>{}</div>".format(title.page_title or title.title)
    html += '\n'.join(
        [div_format.format(**a) for a in messages]
    )
    html += "</body>"
    html += "</html>"

    return html


def generate_html_for_translations(title, page):
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

    for message in messages:
        fragment = fix_html_fragment(message['text'])
        souped_html = _parse_html_for_translation(fragment)
        message['text'] = fix_html_fragment(souped_html)

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


def swap_element(new, old):
    parent = old.getparent()
    index = parent.index(old)
    new.tail = old.tail
    old.tail = None

    parent.insert(index, new)
    parent.remove(old)


def swap_element_inbound(new, old):
    parent = old.getparent()
    if parent.tag == 'div' and 'data-id' in parent.attrib:
        p = old.getprevious()
        new.tail = old.tail
        old.tail = None

        p.append(new)
        parent.remove(old)
    else:
        index = parent.index(old)
        new.tail = old.tail
        old.tail = None

        parent.insert(index, new)
        parent.remove(old)


def _parse_html_for_translation(html):
    """
    This function breaks down anchors and strips them into two divs. This will show up as two strings on transifex.
    :param html:
    :return:
    """
    p = re.compile(r'<.*?>')
    if p.findall(html):

        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        a = CSSSelector('a')
        translatable_a = CSSSelector('a.translatable')
        img = CSSSelector('img:not(.image-translatable)')

        # Translatable anchors are split into text and links
        anchors = translatable_a(tree.getroot())
        for anchor in anchors:
            attributes = [("data-a-{}".format(k), v) for k, v in dict(anchor.attrib).iteritems()]
            div = etree.Element('div')

            content = etree.parse(StringIO("<div class=\"text\">{}</div>".format(stringify_children(anchor)))).getroot()
            href_format = """<div class=\"href\">{}</div>"""
            href_html = fix_html_fragment(href_format.format(anchor.attrib['href']))

            link = etree.parse(StringIO(href_html)).getroot()

            for k, v in attributes:
                div.attrib[k] = v

            div.attrib['class'] = 'former-anchor-translatable'
            div.append(content)
            div.append(link)

            swap_element(div, anchor)

        # Anchors are just the text
        anchors = a(tree.getroot())
        for anchor in anchors:
            attributes = [("data-a-{}".format(k), v) for k, v in dict(anchor.attrib).iteritems()]

            anchor_format = "<div class=\"former-anchor\">{}</div>"
            anchor_html = fix_html_fragment(anchor_format.format(stringify_children(anchor)))

            div = etree.parse(StringIO(anchor_html)).getroot()

            for k, v in attributes:
                div.attrib[k] = v

            swap_element(div, anchor)

        # Images are just copies of the attributes
        images = img(tree.getroot())
        for image in images:
            div = etree.Element('div')
            attributes = [("data-img-{}".format(k), v) for k, v in dict(image.attrib).iteritems()]

            for k, v in attributes:
                div.attrib[k] = v
            div.attrib['class'] = 'former-image'

            swap_element(div, image)
        html = etree.tostring(tree)

    # Chicken coop de grass
    # Massive regex that takes in phone numbers and puts them in divs
    # only to be postprocessed below and dissapear from the translations
    p = re.compile(r'((?:\+\s*)*\d+(?:\s+\(*\d+\)*)*\d+(?:\s+\d+\(*\)*)+|\d+(?:\s+\d+)+|00\d+(?:\s+\d+)+|0\d+(?:\s+\d+)+)')
    html = p.sub('<div class="former-tel">\g<1></div>', html)

    soup = BeautifulSoup(html)
    for div in soup.find_all('div'):
        tag_format = None
        while div.parent.name in ['b', 'em', 'i', 'strong', 'u']:
            if div.parent.name == "b":
                div.parent.unwrap()
                tag_format = "<b>{}</b>"
            if div.parent.name == "strong":
                div.parent.unwrap()
                tag_format = "<strong>{}</strong>"
            if div.parent.name == "em":
                div.parent.unwrap()
                tag_format = "<em>{}</em>"
            if div.parent.name == "i":
                div.parent.unwrap()
                tag_format = "<i>{}</i>"
            if div.parent.name == "u":
                div.parent.unwrap()
                tag_format = "<u>{}</u>"

            if tag_format:
                children = "".join([unicode(c) for c in div.contents])
                div.clear()

                child_soup = BeautifulSoup(tag_format.format(children))
                if child_soup.body:
                    child_frag = child_soup.body.next
                elif child_soup.html:
                    child_frag = child_soup.html.next
                else:
                    child_frag = child_soup
                div.append(child_frag)

    for n in soup.select('u, b, i, em, strong'):
        if not n.text.strip():
            n.extract()

    for tel in soup.select('div.former-tel'):
        number = tel.text
        classes = ['former-tel']
        if tel.select('b'):
            classes.append('has-b')
        if tel.select('em'):
            classes.append('has-em')
        if tel.select('strong'):
            classes.append('has-strong')
        if tel.select('i'):
            classes.append('has-i')
        if tel.select('u'):
            classes.append('has-u')

        tel.attrs['data-tel-number'] = number
        tel.attrs['class'] = classes
        tel.clear()

    return soup.prettify()


def _parse_html_for_content(html):
    """
    This function takes in the HTML from transifex and looks for the special tags that
    break down the anchors into two separate divs see function above
    :param html:
    :return:
    """
    p = re.compile(r'<.*?>')
    if p.findall(html):
        h = html_parser.HTMLParser()
        try:
            parser = etree.XMLParser()
            tree = etree.parse(StringIO(html), parser)
        except Exception as e:
            parser = etree.HTMLParser()
            tree = etree.parse(StringIO(html), parser)

        a = CSSSelector('div.former-anchor')
        translatable_a = CSSSelector('div.former-anchor-translatable')
        img = CSSSelector('div.former-image')
        phones = CSSSelector('div.former-tel')

        anchors = a(tree)
        for anchor in anchors:
            attributes = [(k.replace('data-a-', ''), h.unescape(v)) for k, v in dict(anchor.attrib).iteritems() if
                          'data-a-' in k]

            div = etree.parse(StringIO("<a>{}</a>".format(stringify_children(anchor)))).getroot()
            for k, v in attributes:
                div.attrib[k] = v

            swap_element_inbound(div, anchor)

        anchors = translatable_a(tree.getroot())
        for anchor in anchors:
            attributes = [(k.replace('data-a-', ''), h.unescape(v)) for k, v in dict(anchor.attrib).iteritems() if
                          'data-a-' in k]

            content = etree.Element('div')
            link = etree.Element('div')

            for c in anchor:
                if c.attrib['class'] == 'text':
                    content = c
                if c.attrib['class'] == 'href':
                    link = c

            div = etree.parse(StringIO("<a>{}</a>".format(stringify_children(content)))).getroot()
            for k, v in attributes:
                div.attrib[k] = v

            href = stringify_children(link)

            if href:
                div.attrib['href'] = h.unescape(href)
            swap_element_inbound(div, anchor)

        images = img(tree.getroot())
        for image in images:
            attributes = [(k.replace('data-img-', ''), h.unescape(v)) for k, v in dict(image.attrib).iteritems() if
                          'data-img-' in k]
            div = etree.Element('img')

            for k, v in attributes:
                div.attrib[k] = h.unescape(v)

            swap_element_inbound(div, image)

        tels = phones(tree.getroot())
        for tel in tels:
            classes = tel.attrib['class'].split(' ')
            tag_format = "{}"
            if 'has-b' in classes:
                tag_format = "<b>{}</b>".format(tag_format)
            if 'has-u' in classes:
                tag_format = "<u>{}</u>".format(tag_format)
            if 'has-strong' in classes:
                tag_format = "<strong>{}</strong>".format(tag_format)
            if 'has-em' in classes:
                tag_format = "<em>{}</em>".format(tag_format)
            if 'has-i' in classes:
                tag_format = "<i>{}</i>".format(tag_format)

            tag_format = "<span class=\"tel\">{}</span>".format(tag_format)
            div = etree.parse(StringIO(tag_format.format(tel.attrib['data-tel-number']))).getroot()

            swap_element_inbound(div, tel)
        html = etree.tostring(tree)
        # print(html)
    return html.strip()


def fix_html_fragment(html):
    soup = BeautifulSoup(html)
    return ''.join([unicode(f) for f in soup.body.children]) if soup.body else ''


def _translate_page(dict_list, language, page):
    import cms.api
    h = html_parser.HTMLParser()

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
                        instance.title = h.unescape(strip_html(text)).strip()
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


def stringify_children(node, add_tail=False):
    b = BeautifulSoup(etree.tostring(node))
    tag = node.tag
    bnode = b.find(tag)
    return "".join([unicode(c) for c in bnode.contents])
