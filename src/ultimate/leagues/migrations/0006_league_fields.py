# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0005_auto_20161020_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='fields',
            field=models.ManyToManyField(help_text=b'Select the fields these games will be played at, use the green "+" icon if we\'re playing at a new field.', to='leagues.Field', through='leagues.LeagueFields'),
        ),
    ]
