# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0020_auto_20161025_1229'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='league',
            options={'ordering': ['-year', '-season__order', 'league_start_date']},
        ),
        migrations.AddField(
            model_name='field',
            name='type',
            field=models.CharField(default='', max_length=32, choices=[(b'indoor', b'Indoor'), (b'outdoor', b'Outdoor')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fieldnames',
            name='type',
            field=models.CharField(default='', max_length=32, choices=[(b'grass', b'Grass'), (b'turf', b'Turf')]),
            preserve_default=False,
        ),
    ]
