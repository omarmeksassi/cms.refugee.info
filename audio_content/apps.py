from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.apps import AppConfig

class CustomAppConfig(AppConfig):
    name = 'audio_content'
    verbose_name = 'Audio Content'
