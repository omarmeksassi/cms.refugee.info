from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.conf import settings
from cms.models import Title, Page

from cms_refugeeinfo import celery_app

import requests
from jira import JIRA


SHIM_LANGUAGE_DICTIONARY = {
    'ps': 'af'
}
"""
The Shim above is because django doesnt support Pashto, but Transifex does.
"""


def __get_jira():
    return JIRA(settings.JIRA_URL, basic_auth=(settings.JIRA_USER, settings.JIRA_PASSWORD))


@celery_app.task
def upsert_jira_ticket(page_pk):
    """
    Function that gets called whenever a page is published and it generates a Jira ticket for it.
    :param page_pk: Id of the page
    :return: None
    """
    try:
        page = Page.objects.get(pk=page_pk)
        staging = Title.objects.filter(language='en', slug='staging')
        if staging:
            staging = staging[0].page
        if page in staging.get_descendants():
            page_title = page.get_title_obj('en').page_title
            page_url = page.get_absolute_url('en')
            jira = __get_jira()


            already_started_query = 'status in ("In Translation Review", "In Translation", "In HTML Review") AND "Page Address" ~ "{}"'
            already_started = jira.search_issues(already_started_query.format(page_url))

            for issue in already_started:
                status = issue.fields.status
                jira.transition_issue(issue.id, settings.JIRA_TRANSITIONS['re-edit'])
                jira.add_comment(issue.id, 'Page was in {}, but it was published again by {}'.format(status, page.changed_by))


            editing_query = 'status in ("Editing") AND "Page Address" ~ "{}"'
            editing_query = jira.search_issues(editing_query.format(page_url))
            if not editing_query:
                issue = jira.create_issue(fields={
                    settings.JIRA_PAGE_ADDRESS_FIELD: page_url,
                    'summary': page_title,
                    'project': settings.JIRA_PROJECT,
                    'issuetype': {'id':settings.JIRA_ISSUE_TYPE}
                })

                jira.add_comment(issue.id, 'Page published by {}'.format(page.changed_by))
    except:
        pass

@celery_app.task
def transition_jira_ticket(slug):
    """
    Function that gets called when transifex calls back with a translation ready. If they are all done, it will move the ticket appropriately
    :param slug: slug of the page
    :param language: language sent by transifex, it is not used
    :return:
    """
    try:
        staging = Title.objects.filter(language='en', slug='staging')
        if staging:
            staging = staging[0].page

        titles = Title.objects.filter(language='en', slug=slug, page__in=staging.get_descendants())

        if not titles:
            print('Page not found. Ignoring.')
            return

        page = titles[0].page.get_draft_object()

        password = settings.TRANSIFEX_PASSWORD
        user = settings.TRANSIFEX_USER

        my_url = page.get_absolute_url('en')
        jira = __get_jira()

        transifex_url_data = {
            "project": settings.TRANSIFEX_PROJECT_SLUG,
            "slug": page.get_slug('en'),
        }
        fetch_format = "http://www.transifex.com/api/2/project/{project}/resource/{slug}html/stats/"

        print("Trying to request:", fetch_format.format(**transifex_url_data))
        print("With creds:", user, password)

        r = requests.get(fetch_format.format(**transifex_url_data), auth=(user, password))

        print("Received from transifex:", r.text)
        trans = r.json()

        in_translation = 'status in ("In Translation") AND "Page Address" ~ "{}"'
        in_review = 'status in ("In Translation Review") AND "Page Address" ~ "{}"'

        languages = settings.JIRA_LANGUAGES.split(',')
        reviewed_percentage = set([trans[a]['reviewed_percentage'] for a in languages])
        completed = set([trans[a]['completed'] for a in languages])

        if len(reviewed_percentage) == 1 and list(reviewed_percentage)[0] == '100%':
            print("Pusing to HTML Review")

            jira_issues = jira.search_issues(in_translation.format(my_url))
            for issue in jira_issues:
                jira.transition_issue(issue.id, int(settings.JIRA_TRANSITIONS['translations-complete']))

            jira_issues = jira.search_issues(in_review.format(my_url))
            for issue in jira_issues:
                jira.transition_issue(issue.id, int(settings.JIRA_TRANSITIONS['translations-reviewed']))

        elif len(completed) == 1 and list(completed)[0] == '100%':

            print("Pusing to Translation Review")

            jira_issues = jira.search_issues(in_translation.format(my_url))
            for issue in jira_issues:
                jira.transition_issue(issue.id, int(settings.JIRA_TRANSITIONS['translations-complete']))
    except Exception as e:
        print('Tried to retry it but it still erred out.')
