# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('title_plugin', '0006_alter_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkButtonPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('url', models.URLField(null=True, verbose_name='Url', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AlterField(
            model_name='titleicon',
            name='name',
            field=models.CharField(max_length=250, verbose_name='Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='titleplugin',
            name='icon',
            field=models.ForeignKey(verbose_name='Icon', blank=True, to='title_plugin.TitleIcon', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='titleplugin',
            name='is_important',
            field=models.BooleanField(default=False, verbose_name='Is Important'),
            preserve_default=True,
        ),
    ]
