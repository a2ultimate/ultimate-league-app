# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0021_auto_20160326_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='schedule_note',
            field=models.TextField(help_text=b'note to appear under the schedule', blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='gender',
            field=models.CharField(max_length=1, choices=[(b'F', b'Female'), (b'M', b'Male')]),
        ),
    ]
