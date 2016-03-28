# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0023_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='value',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
    ]
