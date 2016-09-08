# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20160829_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='height_inches',
            field=models.IntegerField(default=0),
        ),
    ]
