from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.db import models
from cms.models import CMSPlugin
from django.utils.translation import ugettext as _


class TocPlugin(CMSPlugin):
    def __unicode__(self):
        return "Table of contents"

class LastUpdatedPlugin(CMSPlugin):
    def __unicode__(self):
        return "Last updated"


class LinkButtonPlugin(CMSPlugin):
    name = models.CharField(max_length=250, verbose_name=_('Name'), )
    url = models.URLField(blank=True, null=True, verbose_name=_('Url'))

    def __unicode__(self):
        return self.name


class TitleIcon(models.Model):
    name = models.CharField(max_length=250, verbose_name=_('Name'))
    icon = models.ImageField(blank=True, null=True, verbose_name=_('Icon'))
    vector_icon = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Vector Icon'))

    def __unicode__(self):
        return self.name


class TitlePlugin(CMSPlugin):
    title = models.CharField(max_length=250, null=False, blank=False, verbose_name=_('Title'))
    is_important = models.BooleanField(default=False, verbose_name=_('Is Important'))
    inherited = models.BooleanField(default=False, verbose_name=_('Inherited'))
    hide_from_toc = models.BooleanField(default=False, verbose_name=_('Hide from Table of Contents'))
    icon = models.ForeignKey(TitleIcon, null=True, blank=True, verbose_name=_('Icon'))
    anchor_name = models.SlugField(max_length=250, null=True, blank=True, verbose_name=_('Custom Anchor Name'))

    def __unicode__(self):
        return self.title


class SoundCloudPlugin(CMSPlugin):
    url = models.URLField(max_length=300, null=True, blank=True, verbose_name=_('SoundCloud Url'))

    def __unicode__(self):
        return "SoundCloud Url: {}".format(self.url)


class NewsFeedPlugin(CMSPlugin):
    url_template = models.CharField(max_length=500, verbose_name=_('URL to RSS feed'))
    number_of_entries = models.PositiveSmallIntegerField(blank=True, null=True, default=3,
                                                         verbose_name=_('Number of Entries'))

    def __unicode__(self):
        return self.url_template