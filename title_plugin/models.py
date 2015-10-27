from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.db import models
from cms.models import CMSPlugin
from django.utils.translation import ugettext as _

class TocPlugin(CMSPlugin):
    def __unicode__(self):
        return "Table of contents"

class TitlePlugin(CMSPlugin):
    title = models.CharField(max_length=250, null=False, blank=False, verbose_name=_('Title'))
    icon = models.ImageField(blank=True, null=True, verbose_name=_('Icon'))

    def __unicode__(self):
        return self.title
