from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.db import models
from cms.models import CMSPlugin
from django.utils.translation import ugettext as _
from django.conf import settings

AUDIO_CONTENT_CHOICES = (
    (1, 'Youtube'),
)


class AudioContent(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Description of the Content'))
    type = models.PositiveIntegerField(blank=True, null=True, choices=AUDIO_CONTENT_CHOICES)

    class Meta:
        verbose_name_plural = _("Audio Content")

    def __unicode__(self):
        return self.name


class AudioContentLanguage(models.Model):
    content = models.ForeignKey(AudioContent, related_name='languages')
    url = models.URLField()
    language = models.CharField(max_length=5, choices=settings.LANGUAGES)

    class Meta:
        verbose_name_plural = _("Audio Content Languages")

    def __unicode__(self):
        return unicode(self.get_language_display())


class AudioContentPlugin(CMSPlugin):
    content = models.ForeignKey(AudioContent)

    def __unicode__(self):
        return u"Audio Content"