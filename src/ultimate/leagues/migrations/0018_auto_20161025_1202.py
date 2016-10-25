# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0017_auto_20161025_1156'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='league',
            name='season',
        ),
        migrations.RenameField(
            model_name='league',
            old_name='season_new',
            new_name='season',
        ),
    ]
