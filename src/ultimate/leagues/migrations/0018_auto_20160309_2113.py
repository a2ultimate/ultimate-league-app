# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_date_of_birth(apps, schema_editor):
    Player = apps.get_model('leagues', 'Player')

    Player.objects.filter(date_of_birth__lte='1800-01-01').update(date_of_birth=None)


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0017_auto_20160309_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='date_of_birth',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.RunPython(update_date_of_birth),
        migrations.AlterField(
            model_name='player',
            name='height_inches',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='highest_level',
            field=models.TextField(null=True, blank=True),
        ),
    ]
