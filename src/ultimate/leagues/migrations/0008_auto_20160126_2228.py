# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0007_auto_20160126_2205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='league',
            old_name='details',
            new_name='detailed_info',
        ),
        migrations.AlterField(
            model_name='league',
            name='gender',
            field=models.CharField(max_length=32, choices=[(b'mens', b"Men's"), (b'mixed', b'Mixed'), (b'open', b'Open'), (b'womens', b"Women's")]),
        ),
        migrations.AlterField(
            model_name='league',
            name='gender_note',
            field=models.TextField(help_text=b'notes for league, e.g. 50-50 league format, showcase league notes'),
        ),
    ]
