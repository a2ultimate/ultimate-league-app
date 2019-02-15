# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0004_auto_20170416_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=8, choices=[(b'html', b'HTML'), (b'markdown', b'Markdown'), (b'plain', b'Plain')])),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('published', models.DateTimeField()),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'news_article',
            },
        ),
    ]
