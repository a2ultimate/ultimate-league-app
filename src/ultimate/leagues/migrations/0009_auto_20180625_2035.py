# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0008_league_num_skip_weeks'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrations',
            name='flagged',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='league',
            name='gender',
            field=models.CharField(max_length=32, choices=[(b'corec', b'Co-Rec'), (b'mens', b"Men's"), (b'mixed', b'Mixed'), (b'open', b'Open'), (b'womens', b"Women's")]),
        ),
    ]
