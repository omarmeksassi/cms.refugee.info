from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'

from django.conf import settings
from cms.models import Title, Page

from cms_refugeeinfo import celery_app

import requests
from jira import JIRA
from StringIO import StringIO
import os
import sys

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
        from content_management import utils as content
        from django.contrib.auth import get_user_model
        User = get_user_model()

        page = Page.objects.get(pk=page_pk)
        staging = Title.objects.filter(language='en', slug='staging')
        production = Title.objects.filter(language='en', slug='production')

        if staging:
            staging = staging[0].page

        if production:
            production = production[0].page

        if page in staging.get_descendants():
            print("In staging")
            page_title = page.get_title_obj('en').page_title or page.get_title_obj('en').title
            page_url = page.get_absolute_url('en')
            jira = __get_jira()

            already_started_query = 'status in ("In Translation Review", "In Translation",' + \
                                    ' "In HTML Review") AND "Page Address" ~ "{}"'
            already_started = jira.search_issues(already_started_query.format(page_url))

            for issue in already_started:
                status = issue.fields.status
                jira.transition_issue(issue.id, settings.JIRA_TRANSITIONS['re-edit'])
                jira.add_comment(issue.id,
                                 'Page was in {}, but it was published again by {}'.format(status, page.changed_by))

            editing_query = 'status in ("Editing") AND "Page Address" ~ "{}"'
            print(editing_query.format(page_url))

            editing_query = jira.search_issues(editing_query.format(page_url))
            print(editing_query)
            if not editing_query:
                issue = jira.create_issue(fields={
                    settings.JIRA_PAGE_ADDRESS_FIELD: page_url,
                    'summary': page_title,
                    'project': settings.JIRA_PROJECT,
                    'issuetype': {'id': settings.JIRA_ISSUE_TYPE}
                })
                print(issue)

                jira.add_comment(issue.id, 'Page published by {}'.format(page.changed_by))
            else:
                issue = editing_query[0]

            # Unassigning issue
            jira.assign_issue(issue.id, None)

            backup_html = StringIO(content.generate_html_for_translations(page.get_title_obj('en'), page))
            jira.add_attachment(issue.id, backup_html, filename="{}.html".format(page.get_slug('en')))

            if production:
                try:
                    source_title = [title for title in Title.objects.filter(slug=page.get_slug('en'), language='en')
                                    if title.page in production.get_descendants()]

                    if source_title:
                        source_title = source_title[0]

                        source_html = content.generate_html_for_diff(title=source_title, language='en')
                        destination_html = content.generate_html_for_diff(title=page.get_title_obj('en'), language='en')

                        import difflib

                        diff_generator = difflib.context_diff(source_html.splitlines(True),
                                                              destination_html.splitlines(True))
                        diff = ''.join(list(diff_generator))

                        jira.add_attachment(issue.id, StringIO(diff),
                                            filename="{}.diff.txt".format(page.get_slug('en')))
                except:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)

            user_query = User.objects.filter(username=page.changed_by)

            if user_query:
                current_user = user_query[0]
                jira_user_query = jira.search_users(current_user.email)
                if jira_user_query:
                    jira_user = jira_user_query[0]
                    jira.assign_issue(issue.id, jira_user.name)
        else:
            print('Not in staging')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        print(e)


@celery_app.task
def transition_jira_ticket(slug, project=settings.TRANSIFEX_PROJECT_SLUG):
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

        # TODO: Refactor
        for k, v in settings.TRANSIFEX_PROJECTS.iteritems():
            if page.get_slug('en') in v:
                if project != k:
                    print("Webhook from wrong project")
                    return

        my_url = page.get_absolute_url('en')
        jira = __get_jira()

        transifex_url_data = {
            "project": project,
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
        import os, sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        print('Tried to retry it but it still erred out.')
