# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0013_baggage_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='group_lock_start_date',
            field=models.DateTimeField(help_text=b'date and time that groups are locked'),
        ),
    ]
