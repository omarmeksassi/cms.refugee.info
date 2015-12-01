# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import *  # NOQA
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect
from django.core import urlresolvers


admin.autodiscover()

from cms.views import details

def landing(request):
    """
    Shim to redirect users to the login page if they try to reach this unauthenticated.
    :param request:
    :return:
    """
    if not request.user.is_anonymous():
        return details(request, '')

    return redirect(urlresolvers.reverse('admin:index'))


urlpatterns = i18n_patterns('',
                            url(r'^admin/', include(admin.site.urls)),  # NOQA
                            url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
                                {'sitemaps': {'cmspages': CMSSitemap}}),
                            url(r'^select2/', include('django_select2.urls')),
                            url(r'^translations/', include('content_management.urls')),
                            url(r'^$', landing),
                            url(r'^', include('cms.urls')),

)


# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = patterns('',
                           url(r'^media/(?P<path>.*)$', 'django.views.static.serve',  # NOQA
                               {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ) + staticfiles_urlpatterns() + urlpatterns  # NOQA
