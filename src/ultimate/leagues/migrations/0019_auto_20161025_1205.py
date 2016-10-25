# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0018_auto_20161025_1202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='league',
            name='season_slug',
        ),
        migrations.AlterField(
            model_name='league',
            name='season',
            field=models.ForeignKey(default=1, to='leagues.Season'),
            preserve_default=False,
        ),
    ]
