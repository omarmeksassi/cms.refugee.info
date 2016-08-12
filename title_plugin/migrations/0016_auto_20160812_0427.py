# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0015_titleplugin_hide_from_toc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titleplugin',
            name='hide_from_toc',
            field=models.BooleanField(default=False, verbose_name='Hide from Table of Contents'),
        ),
    ]
