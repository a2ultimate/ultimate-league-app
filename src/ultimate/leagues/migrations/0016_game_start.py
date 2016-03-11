# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0015_auto_20160227_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='start',
            field=models.DateTimeField(null=True),
        ),
    ]
