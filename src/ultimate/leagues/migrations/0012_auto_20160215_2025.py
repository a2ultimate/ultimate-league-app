# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0011_auto_20160215_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='guardian_name',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='player',
            name='guardian_phone',
            field=models.TextField(blank=True),
        ),
    ]
