# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    def update_date_of_birth(apps, schema_editor):
        Player = apps.get_model('leagues', 'Player')

        Player.objects.filter(date_of_birth='0000-00-00').update(date_of_birth=None)

    dependencies = [
        ('leagues', '0010_auto_20160202_2257'),
    ]

    operations = [
        # migrations.RunPython(update_date_of_birth),
        migrations.AlterField(
            model_name='league',
            name='state',
            field=models.CharField(help_text=b'state of league, changes whether registration is open or league is visible', max_length=32, choices=[(b'closed', b'Closed - visible to all, registration closed to all'), (b'hidden', b'Hidden - hidden to all, registration closed to all'), (b'open', b'Open - visible to all, registration conditionally open to all'), (b'preview', b'Preview - visible only to admins, registration conditionally open only to admins')]),
        ),
        # migrations.AlterField(
        #     model_name='player',
        #     name='date_of_birth',
        #     field=models.DateField(null=True, blank=True),
        # ),
        # migrations.AlterField(
        #     model_name='player',
        #     name='height_inches',
        #     field=models.IntegerField(null=True, blank=True),
        # ),
        # migrations.AlterField(
        #     model_name='player',
        #     name='highest_level',
        #     field=models.TextField(null=True, blank=True),
        # ),
    ]
