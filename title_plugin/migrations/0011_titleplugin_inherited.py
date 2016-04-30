# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0010_lastupdatedplugin'),
    ]

    operations = [
        migrations.AddField(
            model_name='titleplugin',
            name='inherited',
            field=models.BooleanField(default=False, verbose_name='Inherited'),
        ),
    ]
