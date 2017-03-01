# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ultimate.leagues.models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0022_auto_20170228_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='image_cover',
            field=models.ImageField(null=True, upload_to=ultimate.leagues.models.generateLeagueCoverImagePath, blank=True),
        ),
    ]
