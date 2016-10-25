# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0014_auto_20161025_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='season_new',
            field=models.ForeignKey(to='leagues.Season', null=True),
        ),
    ]
