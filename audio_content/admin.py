from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'


from django.contrib import admin
from . import models


class AudioContentLanguageInline(admin.TabularInline):
    model = models.AudioContentLanguage
    extra = 0

class AudioContentAdmin(admin.ModelAdmin):
    inlines = [
        AudioContentLanguageInline,
    ]

admin.site.register(models.AudioContent, AudioContentAdmin)
