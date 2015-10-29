# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0002_auto_20151018_2201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='birthdate',
            new_name='date_of_birth',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='zipcode',
            new_name='zip_code',
        ),
    ]
