# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0011_titleplugin_inherited'),
    ]

    operations = [
        migrations.AddField(
            model_name='titleicon',
            name='vector_icon',
            field=models.CharField(max_length=200, null=True, verbose_name='Vector Icon', blank=True),
        ),
    ]
