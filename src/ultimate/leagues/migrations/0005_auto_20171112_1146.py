# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leagues', '0004_auto_20171112_1138'),
    ]

    operations = [
        migrations.CreateModel(
            name='CouponRedemtion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('redeemed_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-redeemed_at', 'redeemed_by'],
                'db_table': 'coupon_redemption',
            },
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='redeemed_at',
        ),
        migrations.AddField(
            model_name='couponredemtion',
            name='coupon',
            field=models.ForeignKey(to='leagues.Coupon'),
        ),
        migrations.AddField(
            model_name='couponredemtion',
            name='redeemed_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
