# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


def update_registration_dates(apps, schema_editor):
    min_date = datetime.datetime(datetime.MINYEAR, 1, 1)

    Registrations = apps.get_model('leagues', 'Registrations')

    Registrations.objects.filter(created=None, updated=None) \
        .update(
        created=min_date,
        updated=min_date,
        registered=min_date,
        )

def update_registration_dates_again(apps, schema_editor):
    min_date = datetime.datetime(datetime.MINYEAR, 1, 1)

    Registrations = apps.get_model('leagues', 'Registrations')

    Registrations.objects.filter(created=min_date) \
        .update(created=None)
    Registrations.objects.filter(updated=min_date) \
        .update(updated=None)
    Registrations.objects.filter(registered=min_date) \
        .update(registered=None)


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0022_auto_20160327_1916'),
    ]

    operations = [
        migrations.RunPython(update_registration_dates),
        migrations.AlterField(
            model_name='registrations',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='registrations',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RunPython(update_registration_dates_again),
    ]
