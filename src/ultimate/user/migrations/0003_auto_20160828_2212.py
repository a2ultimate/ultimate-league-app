# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0034_auto_20160606_1223'),
        ('user', '0002_auto_20160828_2209'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_count', models.IntegerField(default=0, verbose_name='Post count', blank=True)),
                ('groups', models.TextField()),
                ('nickname', models.CharField(max_length=30)),
                ('date_of_birth', models.DateField(null=True)),
                ('gender', models.CharField(max_length=1, choices=[(b'F', b'Female'), (b'M', b'Male')])),
                ('phone', models.CharField(max_length=15)),
                ('zip_code', models.CharField(max_length=15)),
                ('height_inches', models.IntegerField(null=True, blank=True)),
                ('highest_level', models.TextField(null=True, blank=True)),
                ('jersey_size', models.CharField(max_length=45, choices=[(b'XS', b'XS - Extra Small'), (b'S', b'S - Small'), (b'M', b'M - Medium'), (b'L', b'L - Large'), (b'XL', b'XL -Extra Large'), (b'XXL', b'XXL - Extra Extra Large')])),
                ('guardian_name', models.TextField(blank=True)),
                ('guardian_phone', models.TextField(blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
