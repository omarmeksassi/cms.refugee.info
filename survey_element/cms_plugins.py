from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import SurveyElementPlugin
from django.utils.translation import ugettext as _


class CMSSurveyElementPlugin(CMSPluginBase):
    model = SurveyElementPlugin
    module = _("Survey Element")
    name = _("Survey Element")  # name of the plugin in the interface
    render_template = "survey_element/survey_element.html"

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})

        return context


plugin_pool.register_plugin(CMSSurveyElementPlugin)  # register the plugin
