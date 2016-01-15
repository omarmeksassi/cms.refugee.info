# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('border_closures', '0003_auto_20160114_0114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='border',
            name='enter_country',
            field=django_countries.fields.CountryField(max_length=2, null=True, verbose_name='Entry Country'),
        ),
        migrations.AlterField(
            model_name='border',
            name='exit_country',
            field=django_countries.fields.CountryField(max_length=2, null=True, verbose_name='Exit Country'),
        ),
    ]
