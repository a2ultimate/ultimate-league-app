# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0007_auto_20180502_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='num_skip_weeks',
            field=models.IntegerField(default=0, help_text=b'number of weeks skipped, e.g. skipping 4th of July'),
        ),
    ]
