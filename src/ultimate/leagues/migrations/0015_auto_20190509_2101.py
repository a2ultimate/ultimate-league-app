# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_group_lock_date(apps, schema_editor):
    League = apps.get_model('leagues', 'League')
    League.objects.all().update(
        group_lock_start_date=models.F('waitlist_start_date')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0014_league_group_lock_start_date'),
    ]

    operations = [
        migrations.RunPython(update_group_lock_date),
    ]
