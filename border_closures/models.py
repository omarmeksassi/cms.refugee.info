from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.db import models
from cms.models import CMSPlugin
from django.utils.translation import ugettext as _
from django_countries import fields as country_fields


class Border(models.Model):
    exit_country = country_fields.CountryField(blank=False, null=True, verbose_name=_('Exit Country'))
    enter_country = country_fields.CountryField(blank=False, null=True, verbose_name=_('Entry Country'))

    open_to_others = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = _("Borders")

    def __unicode__(self):
        return "{} -> {}".format(self.exit_country, self.enter_country)


class Nationality(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    country_iso = country_fields.CountryField(blank=True, null=True)

    class Meta:
        verbose_name_plural = _("Nationalities")

    def __unicode__(self):
        return self.name


class BorderNationality(models.Model):
    border = models.ForeignKey(Border, related_name="nationalities")
    nationality = models.ForeignKey(Nationality, related_name="borders")

    open = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = _("Border Nationalities")


    def __unicode__(self):
        return unicode(self.nationality)


class BorderPlugin(CMSPlugin):
    border = models.ForeignKey(Border)

    def __unicode__(self):
        return "Table of contents"

