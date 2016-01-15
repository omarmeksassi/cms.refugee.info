from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import AudioContentPlugin
from django.utils.translation import ugettext as _


class CMSAudioContentPlugin(CMSPluginBase):
    model = AudioContentPlugin
    module = _("Audio Content")
    name = _("Audio Content")  # name of the plugin in the interface
    render_template = "audio_content/audio_content.html"

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})

        return context


plugin_pool.register_plugin(CMSAudioContentPlugin)  # register the plugin
