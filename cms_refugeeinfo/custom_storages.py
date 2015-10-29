from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

import urlparse
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

def domain(url):
    return urlparse.urlparse(url).hostname

class MediaFilesStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs['custom_domain'] = domain(settings.MEDIA_URL)
        super(MediaFilesStorage, self).__init__(*args, **kwargs)

class StaticFilesStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs['custom_domain'] = domain(settings.STATIC_URL)
        super(StaticFilesStorage, self).__init__(*args, **kwargs)