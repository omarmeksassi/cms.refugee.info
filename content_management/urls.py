from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^receive_translation/?', views.receive_translation),
    url(r'^(?P<slug>[a-zA-Z\-0-9]+)/generate-blank/?$', views.generate_blank, ),
    url(r'^(?P<slug>[a-zA-Z\-0-9]+)/pull-from-transifex/(?P<language>[a-zA-z_\-]+)/?$', views.pull_from_transifex, name="pull-from-transifex"),
    url(r'^(?P<slug>[a-zA-Z\-0-9]+)/push-to-transifex/?$', views.push_to_transifex, name="push-to-transifex"),
    url(r'^(?P<slug>[a-zA-Z\-0-9]+)/copy-from-production/?$', views.copy_from_production, name="copy-from-production"),
    url(r'^(?P<slug>[a-zA-Z\-0-9]+)/promote-to-production/?$', views.promote_to_production,
        name="promote-to-production"),


]


