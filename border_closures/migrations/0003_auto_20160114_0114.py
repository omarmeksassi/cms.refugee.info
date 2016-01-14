# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('border_closures', '0002_auto_20160113_1747'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='border',
            options={'verbose_name_plural': 'Borders'},
        ),
        migrations.AlterModelOptions(
            name='bordernationality',
            options={'verbose_name_plural': 'Border Nationalities'},
        ),
        migrations.AlterModelOptions(
            name='nationality',
            options={'verbose_name_plural': 'Nationalities'},
        ),
        migrations.AlterField(
            model_name='border',
            name='enter_country',
            field=django_countries.fields.CountryField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='border',
            name='exit_country',
            field=django_countries.fields.CountryField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='bordernationality',
            name='border',
            field=models.ForeignKey(related_name='nationalities', to='border_closures.Border'),
        ),
        migrations.AlterField(
            model_name='bordernationality',
            name='nationality',
            field=models.ForeignKey(related_name='borders', to='border_closures.Nationality'),
        ),
        migrations.AlterField(
            model_name='nationality',
            name='country_iso',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]
