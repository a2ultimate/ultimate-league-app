# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-10-11 22:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0017_auto_20200204_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrations',
            name='captain',
            field=models.IntegerField(blank=True, choices=[(0, 'I do not want to captain'), (1, 'I will captain'), (2, 'I really want to captain this division')], null=True),
        ),
    ]
