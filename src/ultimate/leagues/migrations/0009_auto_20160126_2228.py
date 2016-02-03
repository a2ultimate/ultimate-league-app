# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0008_auto_20160126_2228'),
    ]

    operations = [
        migrations.RenameField(
            model_name='league',
            old_name='gender_note',
            new_name='summary_info',
        ),
    ]
