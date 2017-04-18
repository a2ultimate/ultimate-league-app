# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StaticContent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=255)),
                ('title', models.CharField(max_length=765)),
                ('content', models.TextField()),
            ],
            options={
                'db_table': 'static_content',
                'verbose_name_plural': 'static content',
            },
        ),
        migrations.CreateModel(
            name='StaticMenuItems',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('location', models.CharField(max_length=32)),
                ('type', models.CharField(max_length=32, choices=[(b'header', 'Header'), (b'external_link', 'External Link'), (b'internal_link', 'Internal Link'), (b'static_link', 'Static Link'), (b'text', 'Text')])),
                ('content', models.CharField(max_length=64)),
                ('href', models.CharField(max_length=255, blank=True)),
                ('position', models.IntegerField()),
                ('parent', models.ForeignKey(default=None, blank=True, to='index.StaticMenuItems', null=True)),
            ],
            options={
                'ordering': ['location', 'parent__id', 'position'],
                'db_table': 'static_menu_items',
                'verbose_name_plural': 'static menu items',
            },
        ),
    ]
