# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_payment_complete(apps, schema_editor):
    Registration = apps.get_model('leagues', 'Registrations')

    for registration in Registration.objects.all():
        registration.payment_complete = registration.check_complete or registration.paypal_complete
        registration.save()

class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0030_registrations_payment_complete'),
    ]

    operations = [
        migrations.RunPython(update_payment_complete),
    ]
