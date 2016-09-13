# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0016_auto_20160812_0427'),
    ]

    operations = [
        migrations.AddField(
            model_name='titleplugin',
            name='position_in_hierarchy',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Position in Hierarchy', choices=[('U', 'Above child content'), ('D', 'Below child content')]),
        ),
    ]
