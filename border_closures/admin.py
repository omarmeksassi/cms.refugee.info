from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'


from django.contrib import admin
from . import models


class BorderNationalityInline(admin.TabularInline):
    model = models.BorderNationality
    extra = 0

class BorderAdmin(admin.ModelAdmin):
    inlines = [
        BorderNationalityInline,
    ]

admin.site.register(models.Border, BorderAdmin)
admin.site.register(models.Nationality, admin.ModelAdmin)
admin.site.register(models.BorderNationality, admin.ModelAdmin)