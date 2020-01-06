# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0015_auto_20190509_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldnames',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
