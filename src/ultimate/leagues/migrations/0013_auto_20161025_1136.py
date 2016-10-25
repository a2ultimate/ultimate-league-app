# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0012_league_tagline'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('slug', models.SlugField()),
                ('order', models.IntegerField(default=None, null=True)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AlterField(
            model_name='league',
            name='night_slug',
            field=models.SlugField(),
        ),
        migrations.AlterField(
            model_name='league',
            name='season_slug',
            field=models.SlugField(),
        ),
    ]
