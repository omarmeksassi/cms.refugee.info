from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = 'reyrodrigues'
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.toolbar.items import Break, SubMenu
from cms.cms_toolbar import PAGE_MENU_IDENTIFIER, ADMINISTRATION_BREAK
from cms import models


@toolbar_pool.register
class ContentToolbar(CMSToolbar):
    def populate(self):
        page = models.Page.objects.get(id=self.toolbar.get_object_pk())
        staging = models.Title.objects.filter(language='en', slug='staging')

        if staging:
            staging = staging[0].page
            if page.id in [p.get_public_object().id for p in staging.get_descendants()]:
                admin_menu = self.toolbar.get_or_create_menu(
                    PAGE_MENU_IDENTIFIER, _('Page')
                )

                #
                # Let's check to see where we would insert an 'Offices' menu in the
                # admin_menu.
                #
                position = admin_menu.get_alphabetical_insert_position(
                    _('Content'),
                    SubMenu
                )

                #
                # If zero was returned, then we know we're the first of our
                # applications' menus to be inserted into the admin_menu, so, here
                # we'll compute that we need to go after the first
                # ADMINISTRATION_BREAK and, we'll insert our own break after our
                # section.
                #
                if not position:
                    # OK, use the ADMINISTRATION_BREAK location + 1
                    position = admin_menu.find_first(
                        Break,
                        identifier=ADMINISTRATION_BREAK
                    ) + 1
                    # Insert our own menu-break, at this new position. We'll insert
                    # all subsequent menus before this, so it will ultimately come
                    # after all of our applications' menus.
                    admin_menu.add_break('custom-break', position=position)

                # OK, create our office menu here.
                content_menu = admin_menu.get_or_create_menu(
                    'content-menu',
                    _('Content ...'),
                    position=position
                )

                # Let's add some sub-menus to our office menu that help our users
                # manage office-related things.

                # Take the user to the admin-listing for offices...
                if self.current_lang == 'en':
                    url = reverse('push-to-transifex', kwargs={'slug': page.get_slug()})
                    content_menu.add_modal_item(_('Send page to be translated'), url=url)
                else:
                    url = reverse('pull-from-transifex',
                                  kwargs={'slug': page.get_slug(), 'language': self.current_lang})
                    content_menu.add_modal_item(_('Download translations'), url=url)

                url = reverse('copy-from-production', kwargs={'slug': page.get_slug()})
                content_menu.add_modal_item(_('Copy from production'), url=url)

                url = reverse('promote-to-production', kwargs={'slug': page.get_slug()})
                content_menu.add_modal_item(_('Promote to production'), url=url)
