# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.template.defaultfilters import slugify


def update_league_slug(apps, schema_editor):
    League = apps.get_model('leagues', 'League')

    for league in League.objects.all():
        league.night_slug = slugify(league.night)
        league.save()


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0004_league_night_slug'),
    ]

    operations = [
        migrations.RunPython(update_league_slug),
    ]
