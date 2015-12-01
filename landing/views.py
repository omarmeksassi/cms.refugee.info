from __future__ import absolute_import, unicode_literals, division, print_function
__author__ = 'reyrodrigues'

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import render, redirect
from django.core import urlresolvers


def landing(request):
    return redirect(urlresolvers.reverse('admin:index'))