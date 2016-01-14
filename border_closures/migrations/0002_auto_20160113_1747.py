# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('border_closures', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='borderplugin',
            name='nationality',
        ),
        migrations.AddField(
            model_name='borderplugin',
            name='border',
            field=models.ForeignKey(default=-1, to='border_closures.Border'),
            preserve_default=False,
        ),
    ]
