# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('title_plugin', '0008_soundcloudplugin'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsFeedPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('url_template', models.CharField(max_length=500, verbose_name='URL to RSS feed')),
                ('number_of_entries', models.PositiveSmallIntegerField(default=3, null=True, verbose_name='Number of Entries', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
