# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey_element', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyelement',
            name='wifi_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='surveyelement',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Description of Survey'),
        ),
    ]
