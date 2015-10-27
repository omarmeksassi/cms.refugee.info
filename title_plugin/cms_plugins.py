from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import TitlePlugin, TocPlugin
from django.utils.translation import ugettext as _


class CMSTocPlugin(CMSPluginBase):
    model = TocPlugin
    module = _("Site Content")
    name = _("Table of contents")  # name of the plugin in the interface
    render_template = "title_plugin/toc_plugin.html"

    def render(self, context, instance, placeholder):
        plugins = list(instance.placeholder.cmsplugin_set.all())
        plugins = [a.titleplugin for a in sorted(plugins, key=lambda p: p.position) if hasattr(a, 'titleplugin')]

        important = [a for a in plugins if a.is_important]
        not_important = [a for a in plugins if not a.is_important]

        context.update({'not_important': not_important, 'important': important})

        return context


class CMSTitlePlugin(CMSPluginBase):
    model = TitlePlugin  # model where plugin data are saved
    module = _("Site Content")
    name = _("Section Title")  # name of the plugin in the interface
    render_template = "title_plugin/title_plugin.html"

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context


plugin_pool.register_plugin(CMSTitlePlugin)  # register the plugin
plugin_pool.register_plugin(CMSTocPlugin)  # register the plugin