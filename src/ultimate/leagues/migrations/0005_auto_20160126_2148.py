# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0004_auto_20151105_2210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='gender',
            field=models.CharField(max_length=32, choices=[(b'50/50', b'50/50 League'), (b'co-ed', b'Normal Co-Ed Gender Matched'), (b'competitive', b'Competitive League'), (b'event', b'Special Event'), (b'hat', b'Hat Tourney'), (b'open', b'Open, No Gender Match'), (b'showcase', b'Showcase League'), (b'women', b'Women Only')]),
        ),
    ]
