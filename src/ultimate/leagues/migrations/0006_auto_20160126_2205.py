# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0005_auto_20160126_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='level',
            field=models.CharField(default='recreational', max_length=32, choices=[(b'competitive', b'Competitive'), (b'recreational', b'Recreational')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='league',
            name='type',
            field=models.CharField(default='league', max_length=32, choices=[(b'event', b'Event'), (b'league', b'League'), (b'tournament', b'Tournament')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='league',
            name='gender',
            field=models.CharField(max_length=32, choices=[(b'50/50', b'50/50 League'), (b'coed', b'Normal Co-Ed Gender Matched'), (b'competitive', b'Competitive League'), (b'event', b'Special Event'), (b'hat', b'Hat Tourney'), (b'open', b'Open, No Gender Match'), (b'showcase', b'Showcase League'), (b'women', b'Women Only'), (b'mens', b"Men's"), (b'mixed', b'Mixed'), (b'open', b'Open'), (b'womens', b"Women's")]),
        ),
        migrations.AlterField(
            model_name='league',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
    ]
