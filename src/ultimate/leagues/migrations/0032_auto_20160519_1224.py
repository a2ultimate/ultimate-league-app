# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0031_auto_20160410_2056'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupon',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='registrations',
            name='registered',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
    ]
