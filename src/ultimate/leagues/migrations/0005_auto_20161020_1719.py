# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0004_auto_20161020_1716'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FieldLeague',
            new_name='LeagueFields',
        ),
    ]
