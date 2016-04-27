# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0027_registrations_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='coupons_accepted',
            field=models.BooleanField(default=True),
        ),
    ]
