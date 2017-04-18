# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_auto_20170416_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticcontent',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 16, 20, 32, 22, 79799), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='staticcontent',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 16, 20, 32, 26, 221448), auto_now=True),
            preserve_default=False,
        ),
    ]
