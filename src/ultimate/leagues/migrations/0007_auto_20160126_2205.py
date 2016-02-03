# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_league_details(apps, schema_editor):
    League = apps.get_model('leagues', 'League')

    for league in League.objects.all():
        if league.gender == '50/50':
            league.gender = 'mixed'
            league.level = 'recreational'
            league.type = 'league'

        elif league.gender == 'coed':
            league.gender = 'mixed'
            league.level = 'recreational'
            league.type = 'league'

        elif league.gender == 'competitive':
            league.gender = 'open'
            league.level = 'competitive'
            league.type = 'league'

        elif league.gender == 'event':
            league.gender = 'mixed'
            league.level = 'recreational'
            league.type = 'event'

        elif league.gender == 'hat':
            league.gender = 'mixed'
            league.level = 'recreational'
            league.type = 'tournament'

        elif league.gender == 'open':
            league.gender = 'open'
            league.level = 'recreational'
            league.type = 'league'

        elif league.gender == 'showcase':
            league.gender = 'open'
            league.level = 'competitive'
            league.type = 'league'

        elif league.gender == 'women':
            league.gender = 'womens'
            league.level = 'recreational'
            league.type = 'league'

        else:
            league.gender = 'mixed'
            league.level = 'recreational'
            league.type = 'event'

        league.save()


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0006_auto_20160126_2205'),
    ]

    operations = [
        migrations.RunPython(set_league_details),
    ]
