# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0001_squashed_0034_auto_20160606_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='teams',
            field=models.ManyToManyField(to='leagues.Team', through='leagues.GameTeams'),
        ),
    ]
