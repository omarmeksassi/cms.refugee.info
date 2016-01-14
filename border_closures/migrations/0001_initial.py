# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='Border',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exit_country', models.CharField(max_length=10, null=True)),
                ('enter_country', models.CharField(max_length=10, null=True)),
                ('open_to_others', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='BorderNationality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('open', models.BooleanField(default=True)),
                ('border', models.ForeignKey(to='border_closures.Border')),
            ],
        ),
        migrations.CreateModel(
            name='BorderPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('country_iso', models.CharField(max_length=5, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='borderplugin',
            name='nationality',
            field=models.ForeignKey(to='border_closures.Nationality'),
        ),
        migrations.AddField(
            model_name='bordernationality',
            name='nationality',
            field=models.ForeignKey(to='border_closures.Nationality'),
        ),
    ]
