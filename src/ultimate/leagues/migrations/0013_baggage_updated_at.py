# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0012_auto_20190217_2259'),
    ]

    operations = [
        migrations.AddField(
            model_name='baggage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
