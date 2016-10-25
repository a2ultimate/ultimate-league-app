# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0015_league_season_new'),
    ]

    operations = [
        migrations.RunSQL('UPDATE league SET season = "winter" WHERE season = "december_youth";'),
        migrations.RunSQL('UPDATE league SET season = "late fall" WHERE season = "Late_Fall";'),
        migrations.RunSQL('UPDATE league SET season = "test" WHERE season = "TEST";'),
        migrations.RunSQL('UPDATE league SET season = "winter" WHERE season = "winter_youth";'),
    ]
