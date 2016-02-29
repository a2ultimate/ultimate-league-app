# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0014_auto_20160227_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='end_time',
            field=models.TimeField(help_text=b'end time for league', null=True),
        ),
        migrations.AddField(
            model_name='league',
            name='num_time_slots',
            field=models.IntegerField(default=1, help_text=b'number of time slots'),
        ),
        migrations.AddField(
            model_name='league',
            name='start_time',
            field=models.TimeField(help_text=b'start time for league', null=True),
        ),
    ]
