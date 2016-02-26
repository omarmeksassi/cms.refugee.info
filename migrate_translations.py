from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.conf import settings

import requests
import json

transifex_strings_url = "https://www.transifex.com/api/2/project/{}/resource/{}/translation/{}/strings/"
transifex_resource_url = "https://www.transifex.com/api/2/project/{}/resources/{}/"
transifex_resources_url = "https://www.transifex.com/api/2/project/{}/resources/"
transifex_content_url = "https://www.transifex.com/api/2/project/{}/resource/{}/content"


def compute_transifex_hash(source_entity, context=''):
    from hashlib import md5

    if isinstance(context, list):
        if context:
            keys = [source_entity] + context
        else:
            keys = [source_entity, '']
    else:
        if context == 'None':
            keys = [source_entity, '']
        else:
            keys = [source_entity, context]
    return md5(':'.join(keys).encode('utf-8')).hexdigest()


auth = (settings.TRANSIFEX_USER, settings.TRANSIFEX_PASSWORD)

r = requests.get(transifex_resources_url.format('refugeeinfo'), auth=auth)
resources = r.json()
for resource in resources:
    resource_content_response = requests.get(transifex_content_url.format('refugeeinfo', resource['slug']), auth=auth)
    resource_content = resource_content_response.json()
    resource.update(resource_content)
    del resource['source_language_code']
    del resource['mimetype']

    check = requests.get(transifex_resource_url.format('refugee-info-irc', resource['slug']), auth=auth)
    is_new = check.status_code == 404

    if not is_new:
        post_response = requests.post(
            transifex_resources_url.format('refugee-info-irc'),
            headers={"Content-type": "application/json"},
            data=json.dumps(resource),
            auth=auth
        )
        print ('New Resource')
    else:
        del resource['i18n_type']
        post_response = requests.post(
            transifex_resources_url.format('refugee-info-irc'),
            headers={"Content-type": "application/json"},
            data=json.dumps(resource),
            auth=auth
        )

        print ('Old Resource')
    if False:
        strings_ar_response = requests.get(transifex_strings_url.format('refugeeinfo', resource['slug'], 'ar'), auth=auth)
        strings_ar = strings_ar_response.json()
        translations = []

        for string_ar in strings_ar:
            hash_ = compute_transifex_hash(string_ar['source_string'])
            translation = string_ar['translation']
            translations.append({"source_entity_hash": hash_, "translation": translation})

        r = requests.put(
            transifex_strings_url.format('refugee-info-irc', resource['slug'], 'ar'),
            headers={"Content-type": "application/json"},
            data=json.dumps(translations),
            auth=auth
        )
        print (r.content)
        strings_fa_response = requests.get(transifex_strings_url.format('refugeeinfo', resource['slug'], 'fa'), auth=auth)
        strings_fa = strings_fa_response.json()
        translations = []

        for string_fa in strings_fa:
            hash_ = compute_transifex_hash(string_fa['source_string'])
            translation = string_fa['translation']
            translations.append({"source_entity_hash": hash_, "translation": translation})

        r = requests.put(
            transifex_strings_url.format('refugee-info-irc', resource['slug'], 'fa'),
            headers={"Content-type": "application/json"},
            data=json.dumps(translations),
            auth=auth
        )
        print (r.content)
    #print (strings_ar_response.content)

r = requests.get(transifex_resources_url.format('refugee-info-irc'), auth=auth)
print(r.content)
