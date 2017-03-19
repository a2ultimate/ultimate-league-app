# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_field_types(apps, schema_editor):
    Field = apps.get_model('leagues', 'Field')
    FieldNames = apps.get_model('leagues', 'FieldNames')

    for field in Field.objects.all():
        if field.id in [1, 15, 18]:
            field.type = 'indoor'
        else:
            field.type = 'outdoor'
        field.save()

    for field_name in FieldNames.objects.all():
        if field_name.field_id in [1, 6, 14, 15, 18]:
            field_name.type = 'turf'
        else:
            field_name.type = 'grass'

        field_name.save()


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0021_auto_20170228_1648'),
    ]

    operations = [
        migrations.RunPython(set_field_types),
    ]
