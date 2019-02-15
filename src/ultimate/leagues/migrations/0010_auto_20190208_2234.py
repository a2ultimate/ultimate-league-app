# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0009_auto_20180625_2035'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registrations',
            options={'ordering': ['-registered', '-updated', '-created'], 'verbose_name_plural': 'registrations'},
        ),
    ]
