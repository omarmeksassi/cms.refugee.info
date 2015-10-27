# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0005_auto_20151027_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titleplugin',
            name='icon',
            field=models.ForeignKey(blank=True, to='title_plugin.TitleIcon', null=True),
            preserve_default=True,
        ),
    ]
