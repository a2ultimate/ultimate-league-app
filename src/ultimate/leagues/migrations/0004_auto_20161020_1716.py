# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0003_auto_20161020_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='league',
            name='fields',
        ),
    ]
