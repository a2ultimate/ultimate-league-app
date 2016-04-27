# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0025_auto_20160327_2226'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='use_count',
            field=models.IntegerField(default=0),
        ),
    ]
