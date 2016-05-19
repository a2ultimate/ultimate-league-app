# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leagues', '0022_auto_20160519_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(help_text=b'Leaving this field empty will generate a random code.', unique=True, max_length=30, blank=True)),
                ('type', models.CharField(max_length=20, choices=[(b'full', b'Full Value'), (b'full', b'Percentage'), (b'full', b'Amount')])),
                ('use_limit', models.IntegerField(default=1)),
                ('value', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('redeemed_at', models.DateTimeField(null=True, blank=True)),
                ('valid_until', models.DateTimeField(help_text=b'Leave empty for coupons that never expire', null=True, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'coupons',
            },
        ),
    ]
