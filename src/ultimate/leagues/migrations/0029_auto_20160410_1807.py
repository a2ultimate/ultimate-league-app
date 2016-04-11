# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0028_league_coupons_accepted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='type',
            field=models.CharField(max_length=20, choices=[(b'full', b'Full Value'), (b'percentage', b'Percentage'), (b'amount', b'Amount')]),
        ),
    ]
