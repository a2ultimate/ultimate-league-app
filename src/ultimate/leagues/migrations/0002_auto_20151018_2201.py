# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='city',
        ),
        migrations.RemoveField(
            model_name='player',
            name='state',
        ),
        migrations.RemoveField(
            model_name='player',
            name='street_address',
        ),
    ]
