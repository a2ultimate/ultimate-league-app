# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0026_coupon_use_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrations',
            name='coupon',
            field=models.ForeignKey(blank=True, to='leagues.Coupon', null=True),
        ),
    ]
