# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0007_auto_20190209_0026'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='newsarticle',
            options={'ordering': ['-published', '-created', '-updated']},
        ),
        migrations.AlterField(
            model_name='newsarticle',
            name='url',
            field=models.SlugField(null=True, blank=True),
        ),
    ]
