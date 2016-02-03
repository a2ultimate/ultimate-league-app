# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0009_auto_20160126_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='state',
            field=models.CharField(help_text=b'state of league, changes whether registration is open or league is visible', max_length=32, choices=[(b'CLOSED', b'Closed - visible to all, registration closed to all'), (b'HIDDEN', b'Hidden - hidden to all, registration closed to all'), (b'OPEN', b'Open - visible to all, registration conditionally open to all'), (b'PREVIEW', b'Preview - visible only to admins, registration conditionally open only to admins')]),
        ),
        migrations.AlterField(
            model_name='player',
            name='date_of_birth',
            field=models.DateField(help_text=b'e.g. 2016-02-02'),
        ),
    ]
