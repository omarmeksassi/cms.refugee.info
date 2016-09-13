from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import TitlePlugin, LastUpdatedPlugin, TocPlugin, LinkButtonPlugin, SoundCloudPlugin, NewsFeedPlugin
from django.utils.translation import ugettext as _
import feedparser
from django.utils.translation import get_language


class CMSLastUpdatedPlugin(CMSPluginBase):
    model = LastUpdatedPlugin
    module = _("Site Content")
    name = _("Last Updated")  # name of the plugin in the interface
    render_template = "title_plugin/last_updated_plugin.html"

    def render(self, context, instance, placeholder):
        if instance.page.publisher_public:
            publication_date = instance.page.publisher_public.changed_date
        else:
            publication_date = instance.page.creation_date

        context.update({
            'publication_date': publication_date
        })
        return context


class CMSTocPlugin(CMSPluginBase):
    model = TocPlugin
    module = _("Site Content")
    name = _("Table of contents")  # name of the plugin in the interface
    render_template = "title_plugin/toc_plugin.html"

    def render(self, context, instance, placeholder):
        plugins = list(instance.placeholder.cmsplugin_set.all())
        plugins = [a for a in plugins if a.language == instance.language]
        plugins = [a.get_plugin_instance()[0] for a in sorted(plugins, key=lambda p: p.position)
                   if type(a.get_plugin_instance()[1]) is CMSTitlePlugin]

        important = [a for a in plugins if a.is_important if a]
        not_important = [a for a in plugins if not a.is_important if a]

        context.update({'not_important': not_important, 'important': important})

        return context


class CMSTitlePlugin(CMSPluginBase):
    model = TitlePlugin  # model where plugin data are saved
    module = _("Site Content")
    name = _("Section Title")  # name of the plugin in the interface
    render_template = "title_plugin/title_plugin.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


class CMSNewsFeedPlugin(CMSPluginBase):
    model = NewsFeedPlugin  # model where plugin data are saved
    module = _("Site Content")
    name = _("News Feed")  # name of the plugin in the interface
    render_template = "title_plugin/news_feed_plugin.html"

    def render(self, context, instance, placeholder):
        full_url = instance.url_template.format(**{
            'LANGUAGE_CODE': get_language()
        })
        feed = feedparser.parse(full_url)
        num_entries = instance.number_of_entries or 3
        entries = sorted(feed['entries'][0:num_entries], key=lambda e: e['published_parsed'], reverse=True)

        context.update({'instance': instance, 'entries': entries})
        return context


class CMSLinkButtonPlugin(CMSPluginBase):
    model = LinkButtonPlugin  # model where plugin data are saved
    module = _("Site Content")
    name = _("Link Button")  # name of the plugin in the interface
    render_template = "title_plugin/link_button.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


class CMSSoundCloudPlugin(CMSPluginBase):
    model = SoundCloudPlugin  # model where plugin data are saved
    module = _("Site Content")
    name = _("SoundClound File")  # name of the plugin in the interface
    render_template = "soundcloud_plugin/soundcloud_plugin.html"
    text_enabled = False

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context

plugin_pool.register_plugin(CMSLastUpdatedPlugin)
plugin_pool.register_plugin(CMSNewsFeedPlugin)  # register the plugin
plugin_pool.register_plugin(CMSTitlePlugin)  # register the plugin
plugin_pool.register_plugin(CMSTocPlugin)  # register the plugin
plugin_pool.register_plugin(CMSLinkButtonPlugin)  # register the plugin
plugin_pool.register_plugin(CMSSoundCloudPlugin)  # register the plugin