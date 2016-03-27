# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0019_auto_20160309_2117'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='league',
            name='league_captains_email',
        ),
        migrations.RemoveField(
            model_name='league',
            name='league_email',
        ),
        migrations.AddField(
            model_name='league',
            name='division_captains_email',
            field=models.CharField(help_text=b'email address for league captains', max_length=64, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='league',
            name='division_email',
            field=models.CharField(help_text=b'email address for just this league', max_length=64, null=True, blank=True),
        ),
    ]
