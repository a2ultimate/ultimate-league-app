# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0010_auto_20190208_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='registration_prompt',
            field=models.TextField(help_text=b'prompt to show during registration, e.g. to collect data around format preference', blank=True),
        ),
        migrations.AddField(
            model_name='registrations',
            name='prompt_response',
            field=models.CharField(help_text=b'response to the registration prompt for a division', max_length=255, null=True, blank=True),
        ),
    ]
