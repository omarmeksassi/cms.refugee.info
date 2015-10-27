# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('title_plugin', '0004_titleplugin_is_important'),
    ]

    operations = [
        migrations.CreateModel(
            name='TitleIcon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('icon', models.ImageField(upload_to=b'', null=True, verbose_name='Icon', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='titleplugin',
            name='icon',
            field=models.ForeignKey(blank=True, to='title_plugin.TitleIcon', null=True),
            preserve_default=True,
        ),
    ]
