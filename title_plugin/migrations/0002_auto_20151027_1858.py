# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='titleplugin',
            name='icon',
            field=models.ImageField(upload_to=b'', null=True, verbose_name='Icon', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='titleplugin',
            name='title',
            field=models.CharField(max_length=250, verbose_name='Title'),
            preserve_default=True,
        ),
    ]
