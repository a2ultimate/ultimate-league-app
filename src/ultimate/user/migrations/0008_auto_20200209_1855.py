# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-09 18:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20200209_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerconcussionwaiver',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
