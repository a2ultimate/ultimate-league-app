# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0008_auto_20161019_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='night_slug',
            field=models.SlugField(default=None, editable=False),
            preserve_default=False,
        ),
    ]
