# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0019_auto_20161025_1205'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='league',
            options={'ordering': ['year', 'season__order', 'league_start_date']},
        ),
    ]
