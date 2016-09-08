# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection, migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0033_auto_20160604_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='level',
            field=models.CharField(max_length=32, choices=[(b'comp', b'Competitive'), (b'rec', b'Recreational'), (b'youth', b'Youth')]),
        ),
        migrations.RunSQL('UPDATE league SET level = "comp" WHERE level = "competitive";'),
        migrations.RunSQL('UPDATE league SET level = "rec" WHERE level = "recreational";'),
    ]
