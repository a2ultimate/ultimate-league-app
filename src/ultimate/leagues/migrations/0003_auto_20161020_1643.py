# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0002_game_teams'),
    ]

    operations = [
        migrations.RenameField(
            model_name='league',
            old_name='field',
            new_name='fields',
        ),
    ]
