# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0005_auto_20171112_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='captaining_note',
            field=models.TextField(help_text=b'note for captaining, typically captain meeting date and time', blank=True),
        ),
    ]
