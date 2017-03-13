# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0022_auto_20170228_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='group_id',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
