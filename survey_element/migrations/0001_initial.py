# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyElement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Description of the Content')),
            ],
            options={
                'verbose_name_plural': 'Survey Element',
            },
        ),
        migrations.CreateModel(
            name='SurveyElementLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('language', models.CharField(max_length=5, choices=[(b'en', b'English'), (b'ar', b'Arabic'), (b'fa', b'Farsi'), (b'af', b'Pashto'), (b'el', b'Greek')])),
                ('content', models.ForeignKey(related_name='languages', to='survey_element.SurveyElement')),
            ],
            options={
                'verbose_name_plural': 'Survey Element Languages',
            },
        ),
        migrations.CreateModel(
            name='SurveyElementPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('content', models.ForeignKey(to='survey_element.SurveyElement')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
