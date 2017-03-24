# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0023_auto_20170312_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='min_age',
            field=models.IntegerField(default=0, help_text=b'minimum age (in years)'),
        ),
    ]
