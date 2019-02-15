# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0005_newsarticle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='url',
            field=models.SlugField(),
        ),
    ]
