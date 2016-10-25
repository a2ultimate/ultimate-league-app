# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_league_season_new(apps, schema_editor):
    League = apps.get_model('leagues', 'League')
    Season = apps.get_model('leagues', 'Season')

    for league in League.objects.all():
        league.season_new = Season.objects.get(name=league.season)
        league.save()


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0016_auto_20161025_1153'),
    ]

    operations = [
        migrations.RunPython(update_league_season_new),
    ]
