from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<slug>[a-zA-Z\-0-9]+)/generate-blank/?$', views.generate_blank, ),
    url(r'^(?P<slug>[a-zA-Z\-0-9]+)/upload-translations/?$', views.upload_translations, ),

]


