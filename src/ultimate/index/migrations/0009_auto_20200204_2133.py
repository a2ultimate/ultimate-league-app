# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-04 21:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0008_auto_20190214_2244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='type',
            field=models.CharField(choices=[('html', 'HTML'), ('markdown', 'Markdown'), ('plain', 'Plain')], max_length=8),
        ),
        migrations.AlterField(
            model_name='staticcontent',
            name='type',
            field=models.CharField(choices=[('html', 'HTML'), ('markdown', 'Markdown'), ('plain', 'Plain')], max_length=32),
        ),
        migrations.AlterField(
            model_name='staticmenuitems',
            name='type',
            field=models.CharField(choices=[('header', 'Header'), ('external_link', 'External Link'), ('internal_link', 'Internal Link'), ('static_link', 'Static Link'), ('text', 'Text')], max_length=32),
        ),
    ]
