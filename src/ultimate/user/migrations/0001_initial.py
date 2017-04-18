# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name='email address', db_index=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into the admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'swappable': 'AUTH_USER_MODEL',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_count', models.IntegerField(default=0, verbose_name='Post count', blank=True)),
                ('groups', models.TextField()),
                ('nickname', models.CharField(max_length=30, blank=True)),
                ('date_of_birth', models.DateField(null=True, blank=True)),
                ('gender', models.CharField(max_length=1, choices=[(b'F', b'Female'), (b'M', b'Male')])),
                ('phone', models.CharField(max_length=15, blank=True)),
                ('zip_code', models.CharField(max_length=15, blank=True)),
                ('height_inches', models.IntegerField(default=0)),
                ('highest_level', models.TextField(blank=True)),
                ('jersey_size', models.CharField(blank=True, max_length=45, choices=[(b'XS', b'XS - Extra Small'), (b'S', b'S - Small'), (b'M', b'M - Medium'), (b'L', b'L - Large'), (b'XL', b'XL -Extra Large'), (b'XXL', b'XXL - Extra Extra Large')])),
                ('guardian_name', models.TextField(blank=True)),
                ('guardian_phone', models.TextField(blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'permissions': (('block_users', 'Can block any user'),),
            },
        ),
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
