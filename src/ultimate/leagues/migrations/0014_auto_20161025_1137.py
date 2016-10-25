# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0013_auto_20161025_1136'),
    ]

    operations = [
        migrations.RunSQL('INSERT INTO leagues_season (`name`, `slug`, `order`) VALUES ("Test", "test", 0);'),
        migrations.RunSQL('INSERT INTO leagues_season (`name`, `slug`, `order`) VALUES ("Winter", "winter", 1);'),
        migrations.RunSQL('INSERT INTO leagues_season (`name`, `slug`, `order`) VALUES ("Spring", "spring", 2);'),
        migrations.RunSQL('INSERT INTO leagues_season (`name`, `slug`, `order`) VALUES ("Summer", "summer", 3);'),
        migrations.RunSQL('INSERT INTO leagues_season (`name`, `slug`, `order`) VALUES ("Fall", "fall", 4);'),
        migrations.RunSQL('INSERT INTO leagues_season (`name`, `slug`, `order`) VALUES ("Late Fall", "late-fall", 5);'),
    ]
