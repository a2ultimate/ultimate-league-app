# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.template.defaultfilters import slugify


def update_league_slug(apps, schema_editor):
    League = apps.get_model('leagues', 'League')

    for league in League.objects.all():
        league.season_slug = slugify(league.season)
        league.save()

class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0007_league_season_slug'),
    ]

    operations = [
        migrations.RunPython(update_league_slug),
    ]
