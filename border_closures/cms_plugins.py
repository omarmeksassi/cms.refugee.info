from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import BorderPlugin
from django.utils.translation import ugettext as _


class CMSBorderClosurePlugin(CMSPluginBase):
    model = BorderPlugin
    module = _("Border Closures")
    name = _("Border dashboard")  # name of the plugin in the interface
    render_template = "border_closures/dashboard.html"

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})

        return context


plugin_pool.register_plugin(CMSBorderClosurePlugin)  # register the plugin
