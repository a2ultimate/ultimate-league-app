# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0032_auto_20160519_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='level',
            field=models.CharField(max_length=32, choices=[(b'competitive', b'Competitive'), (b'recreational', b'Recreational'), (b'youth', b'Youth')]),
        ),
    ]
