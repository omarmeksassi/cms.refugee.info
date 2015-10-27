# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0003_tocplugin'),
    ]

    operations = [
        migrations.AddField(
            model_name='titleplugin',
            name='is_important',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
