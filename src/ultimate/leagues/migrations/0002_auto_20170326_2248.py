# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='team',
            name='league',
            field=models.ForeignKey(to='leagues.League'),
        ),
        migrations.AddField(
            model_name='registrations',
            name='baggage',
            field=models.ForeignKey(blank=True, to='leagues.Baggage', null=True),
        ),
        migrations.AddField(
            model_name='registrations',
            name='coupon',
            field=models.ForeignKey(blank=True, to='leagues.Coupon', null=True),
        ),
        migrations.AddField(
            model_name='registrations',
            name='league',
            field=models.ForeignKey(to='leagues.League'),
        ),
        migrations.AddField(
            model_name='registrations',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='leaguefields',
            name='field',
            field=models.ForeignKey(to='leagues.Field'),
        ),
        migrations.AddField(
            model_name='leaguefields',
            name='league',
            field=models.ForeignKey(to='leagues.League'),
        ),
        migrations.AddField(
            model_name='league',
            name='fields',
            field=models.ManyToManyField(help_text=b'Select the fields these games will be played at, use the green "+" icon if we\'re playing at a new field.', to='leagues.Field', through='leagues.LeagueFields'),
        ),
        migrations.AddField(
            model_name='league',
            name='season',
            field=models.ForeignKey(to='leagues.Season'),
        ),
        migrations.AddField(
            model_name='gameteams',
            name='game',
            field=models.ForeignKey(to='leagues.Game'),
        ),
        migrations.AddField(
            model_name='gameteams',
            name='team',
            field=models.ForeignKey(to='leagues.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='field_name',
            field=models.ForeignKey(to='leagues.FieldNames'),
        ),
        migrations.AddField(
            model_name='game',
            name='league',
            field=models.ForeignKey(to='leagues.League'),
        ),
        migrations.AddField(
            model_name='game',
            name='teams',
            field=models.ManyToManyField(to='leagues.Team', through='leagues.GameTeams'),
        ),
        migrations.AddField(
            model_name='fieldnames',
            name='field',
            field=models.ForeignKey(to='leagues.Field'),
        ),
        migrations.AddField(
            model_name='coupon',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='registrations',
            unique_together=set([('user', 'league')]),
        ),
    ]
