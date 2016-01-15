# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Description of the Content')),
                ('type', models.PositiveIntegerField(blank=True, null=True, choices=[(1, 'Youtube')])),
            ],
            options={
                'verbose_name_plural': 'Audio Content',
            },
        ),
        migrations.CreateModel(
            name='AudioContentLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('language', models.CharField(max_length=5, choices=[(b'en', b'English'), (b'ar', b'Arabic'), (b'fa', b'Farsi'), (b'af', b'Pashto'), (b'el', b'Greek')])),
                ('content', models.ForeignKey(related_name='languages', to='audio_content.AudioContent')),
            ],
            options={
                'verbose_name_plural': 'Audio Content Languages',
            },
        ),
        migrations.CreateModel(
            name='AudioContentPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('content', models.ForeignKey(to='audio_content.AudioContent')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
