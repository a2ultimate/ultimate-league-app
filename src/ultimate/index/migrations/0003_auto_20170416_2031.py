# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_staticcontent_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticcontent',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='staticcontent',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
