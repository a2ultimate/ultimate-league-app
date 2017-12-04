# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0003_auto_20170417_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='note',
            field=models.TextField(help_text=b'What is the coupon for?', blank=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='use_count',
            field=models.IntegerField(default=0, help_text=b'How many times the coupon has been used'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='use_limit',
            field=models.IntegerField(default=1, help_text=b'How many uses the coupon should have'),
        ),
    ]
