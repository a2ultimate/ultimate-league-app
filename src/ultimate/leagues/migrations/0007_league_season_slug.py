# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0006_league_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='season_slug',
            field=models.SlugField(default=None, editable=False),
            preserve_default=False,
        ),
    ]
