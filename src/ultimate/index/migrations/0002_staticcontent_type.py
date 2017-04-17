# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticcontent',
            name='type',
            field=models.CharField(default='html', max_length=32, choices=[(b'html', b'HTML'), (b'markdown', b'Markdown'), (b'plain', b'Plain')]),
            preserve_default=False,
        ),
    ]
