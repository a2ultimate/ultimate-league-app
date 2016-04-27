# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0024_auto_20160327_2226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
