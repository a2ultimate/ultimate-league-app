# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0011_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='tagline',
            field=models.TextField(help_text=b'short tagline for description fields, e.g. SEO, Facebook, etc.', blank=True),
        ),
    ]
