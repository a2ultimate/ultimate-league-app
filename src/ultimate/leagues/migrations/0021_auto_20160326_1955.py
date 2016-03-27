# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0020_auto_20160326_1954'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='division_captains_email_group_id',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='league',
            name='division_email_group_id',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
