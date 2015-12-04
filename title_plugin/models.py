from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.db import models
from cms.models import CMSPlugin
from django.utils.translation import ugettext as _


class TocPlugin(CMSPlugin):
    def __unicode__(self):
        return "Table of contents"


class LinkButtonPlugin(CMSPlugin):
    name = models.CharField(max_length=250, verbose_name=_('Name'), )
    url = models.URLField(blank=True, null=True, verbose_name=_('Url'))

    def __unicode__(self):
        return self.name


class TitleIcon(models.Model):
    name = models.CharField(max_length=250, verbose_name=_('Name'))
    icon = models.ImageField(blank=True, null=True, verbose_name=_('Icon'))

    def __unicode__(self):
        return self.name


class TitlePlugin(CMSPlugin):
    title = models.CharField(max_length=250, null=False, blank=False, verbose_name=_('Title'))
    is_important = models.BooleanField(default=False, verbose_name=_('Is Important'))
    icon = models.ForeignKey(TitleIcon, null=True, blank=True, verbose_name=_('Icon'))

    def __unicode__(self):
        return self.title

class SoundCloudPlugin(CMSPlugin):
    url = models.URLField(max_length=300, null=True, blank=True, verbose_name=_('SoundCloud Url'))

    def __unicode__(self):
        return "SoundCloud Url: {}".format(self.url)