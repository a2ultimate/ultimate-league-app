# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0034_auto_20160606_1223'),
        ('user', '0003_auto_20160828_2212'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerRatings',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('experience', models.PositiveIntegerField(default=None, null=True, blank=True, choices=[(1, b'I am new to ultimate or have played less than 2 years of pickup.'), (2, b'I have played in an organized league or on a high school team for 1-2 seasons, or pickup for 3+ years.'), (3, b'I have played in an organized league or on a high school team for 3+ seasons.'), (4, b'I have played on a college or club team in the last 6 years.'), (5, b'I have played multiple seasons on a college or club team in the last 4 years.'), (6, b'I have played multiple seasons on a regionals or nationals-level college or club team in the last 4 years.')])),
                ('strategy', models.PositiveIntegerField(default=None, null=True, blank=True, choices=[(1, b'I am new to organized ultimate.'), (2, b'I have basic knowledge of the game (e.g. stall counts, pivoting).'), (3, b'I have moderate knowledge (e.g. vertical stack, force, basic man defense).'), (4, b'I have advanced knowledge (e.g. zone defense, horizontal stack, switching).'), (5, b'I am familiar enough with the above concepts that I could explain them to a new player.'), (6, b'I would consider myself an expert in ultimate strategy.')])),
                ('throwing', models.PositiveIntegerField(default=None, null=True, blank=True, choices=[(1, b'I am a novice or am learning to throw.'), (2, b'I can throw a backhand 10 yards with 90% confidence.'), (3, b'I can throw a forehand 10+ yards with 90% confidence and can handle if needed.'), (4, b'I am confident throwing forehand and backhand various distances and can handle at a league level.'), (5, b'I am confident throwing break throws and can be a very good league-level handler.'), (6, b'I am confident in many styles of throws and could be a college or club-level handler.')])),
                ('athleticism', models.PositiveIntegerField(default=None, null=True, blank=True, choices=[(1, b'I am slow, it is hard to change direction, and am easily winded.'), (2, b'I can change direction decently, but need to rest often.'), (3, b'I am somewhat fast, can make hard cuts, and can play for a few minutes at a time before resting.'), (4, b'I am fairly fast, can change direction and react well, and can play a few hard points in a row.'), (5, b'I am very fast, can turn well, jump high, and need little rest.'), (6, b'I am faster than anyone on the field at any level and enjoy playing almost every point.')])),
                ('competitiveness', models.PositiveIntegerField(default=None, null=True, blank=True, choices=[(1, b'I do not care whether I win or lose, I play purely to socialize and have fun.'), (2, b'I play ultimate to have fun, but would prefer to win.'), (3, b'I am competitive, fight to win close games, and am somewhat disappointed by a loss.'), (4, b'I am extremely competitive and am very disappointed by a loss.')])),
                ('spirit', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('ratings_type', models.PositiveIntegerField(choices=[(1, b'Captain'), (2, b'Junta'), (3, b'User')])),
                ('not_sure', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'player ratings',
            },
        ),
        migrations.CreateModel(
            name='PlayerRatingsReport',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('updated', models.DateTimeField()),
                ('submitted_by', models.ForeignKey(related_name='ratings_report_submitted_by_set', to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(to='leagues.Team')),
            ],
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'permissions': (('block_users', 'Can block any user'),)},
        ),
        migrations.AddField(
            model_name='playerratings',
            name='ratings_report',
            field=models.ForeignKey(blank=True, to='user.PlayerRatingsReport', null=True),
        ),
        migrations.AddField(
            model_name='playerratings',
            name='submitted_by',
            field=models.ForeignKey(related_name='ratings_submitted_by_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='playerratings',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
