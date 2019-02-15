# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0006_auto_20190208_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='url',
            field=models.SlugField(null=True),
        ),
    ]
