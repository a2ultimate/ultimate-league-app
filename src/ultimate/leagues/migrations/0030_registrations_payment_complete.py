# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0029_auto_20160410_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrations',
            name='payment_complete',
            field=models.BooleanField(default=False),
        ),
    ]
