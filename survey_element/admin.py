from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'


from django.contrib import admin
from . import models


class SurveyElementLanguageInline(admin.TabularInline):
    model = models.SurveyElementLanguage
    extra = 0

class SurveyElementAdmin(admin.ModelAdmin):
    inlines = [
        SurveyElementLanguageInline,
    ]

admin.site.register(models.SurveyElement, SurveyElementAdmin)
