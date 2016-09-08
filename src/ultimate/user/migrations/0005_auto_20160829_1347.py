# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20160828_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='date_of_birth',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='height_inches',
            field=models.IntegerField(default=0, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='player',
            name='highest_level',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='player',
            name='jersey_size',
            field=models.CharField(blank=True, max_length=45, choices=[(b'XS', b'XS - Extra Small'), (b'S', b'S - Small'), (b'M', b'M - Medium'), (b'L', b'L - Large'), (b'XL', b'XL -Extra Large'), (b'XXL', b'XXL - Extra Extra Large')]),
        ),
        migrations.AlterField(
            model_name='player',
            name='nickname',
            field=models.CharField(max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='phone',
            field=models.CharField(max_length=15, blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='zip_code',
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
