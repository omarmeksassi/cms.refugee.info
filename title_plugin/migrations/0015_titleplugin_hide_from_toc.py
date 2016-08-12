# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0014_auto_20160720_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='titleplugin',
            name='hide_from_toc',
            field=models.NullBooleanField(default=False, verbose_name='Hide from Table of Contents'),
        ),
    ]
