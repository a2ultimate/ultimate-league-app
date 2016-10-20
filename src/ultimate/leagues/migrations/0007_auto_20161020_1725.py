# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0006_league_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='leaguefields',
            options={'verbose_name_plural': 'league fields'},
        ),
    ]
