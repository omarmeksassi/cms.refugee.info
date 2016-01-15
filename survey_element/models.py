from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.db import models
from cms.models import CMSPlugin
from django.utils.translation import ugettext as _
from django.conf import settings

class SurveyElement(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Description of Survey'))

    class Meta:
        verbose_name_plural = _("Survey Element")

    def __unicode__(self):
        return self.name


class SurveyElementLanguage(models.Model):
    content = models.ForeignKey(SurveyElement, related_name='languages')
    url = models.URLField()
    language = models.CharField(max_length=5, choices=settings.LANGUAGES)

    class Meta:
        verbose_name_plural = _("Survey Element Languages")

    def __unicode__(self):
        return unicode(self.get_language_display())


class SurveyElementPlugin(CMSPlugin):
    content = models.ForeignKey(SurveyElement)

    def __unicode__(self):
        return u"Survey Element"