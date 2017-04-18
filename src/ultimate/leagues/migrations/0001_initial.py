# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ultimate.leagues.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Baggage',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'baggage',
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(help_text=b'Leaving this field empty will generate a random code.', unique=True, max_length=30, blank=True)),
                ('type', models.CharField(max_length=20, choices=[(b'full', b'Full Value'), (b'percentage', b'Percentage'), (b'amount', b'Amount')])),
                ('use_count', models.IntegerField(default=0)),
                ('use_limit', models.IntegerField(default=1)),
                ('value', models.IntegerField(default=None, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('redeemed_at', models.DateTimeField(null=True, blank=True)),
                ('valid_until', models.DateTimeField(help_text=b'Leave empty for coupons that never expire', null=True, blank=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'db_table': 'coupons',
            },
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('layout_link', models.TextField(blank=True)),
                ('address', models.TextField(blank=True)),
                ('driving_link', models.TextField(blank=True)),
                ('note', models.TextField(blank=True)),
                ('type', models.CharField(max_length=32, choices=[(b'indoor', b'Indoor'), (b'outdoor', b'Outdoor')])),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'field',
            },
        ),
        migrations.CreateModel(
            name='FieldNames',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('type', models.CharField(max_length=32, choices=[(b'grass', b'Grass'), (b'turf', b'Turf')])),
            ],
            options={
                'ordering': ['field__name', 'name'],
                'db_table': 'field_names',
                'verbose_name_plural': 'field names',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.DateField()),
                ('start', models.DateTimeField(null=True)),
            ],
            options={
                'ordering': ['-date', 'field_name'],
                'db_table': 'game',
            },
        ),
        migrations.CreateModel(
            name='GameTeams',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'game_teams',
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(help_text=b'four digit year, e.g. 2013')),
                ('night', models.CharField(help_text=b'lower case, no special characters, e.g. "sunday", "tuesday and thursday", "end of season tournament"', max_length=32)),
                ('night_slug', models.SlugField()),
                ('gender', models.CharField(max_length=32, choices=[(b'mens', b"Men's"), (b'mixed', b'Mixed'), (b'open', b'Open'), (b'womens', b"Women's")])),
                ('level', models.CharField(max_length=32, choices=[(b'comp', b'Competitive'), (b'rec', b'Recreational'), (b'youth', b'Youth')])),
                ('type', models.CharField(max_length=32, choices=[(b'event', b'Event'), (b'league', b'League'), (b'tournament', b'Tournament')])),
                ('tagline', models.TextField(help_text=b'short tagline for description fields, e.g. SEO, Facebook, etc.', blank=True)),
                ('summary_info', models.TextField(help_text=b'notes for league, e.g. 50-50 league format, showcase league notes')),
                ('detailed_info', models.TextField(help_text=b'details page text, use HTML')),
                ('times', models.TextField(help_text=b'start to end time, e.g. 6:00-8:00pm')),
                ('start_time', models.TimeField(help_text=b'start time for league', null=True)),
                ('end_time', models.TimeField(help_text=b'end time for league', null=True)),
                ('num_time_slots', models.IntegerField(default=1, help_text=b'number of time slots')),
                ('schedule_note', models.TextField(help_text=b'note to appear under the schedule', blank=True)),
                ('num_games_per_week', models.IntegerField(default=1, help_text=b'number of games per week, used to calculate number of games for a league')),
                ('reg_start_date', models.DateTimeField(help_text=b'date and time that registration process is open (not currently automated)')),
                ('price_increase_start_date', models.DateTimeField(help_text=b'date and time when cost increases for league')),
                ('waitlist_start_date', models.DateTimeField(help_text=b'date and time that waitlist is started (regardless of number of registrations)')),
                ('league_start_date', models.DateField(help_text=b'date of first game')),
                ('league_end_date', models.DateField(help_text=b'date of last game')),
                ('max_players', models.IntegerField(help_text=b'max players for league, extra registrations will be placed on waitlist')),
                ('baggage', models.IntegerField(help_text=b'max baggage group size')),
                ('min_age', models.IntegerField(default=0, help_text=b'minimum age (in years)')),
                ('paypal_cost', models.IntegerField(help_text=b'base cost of league if paying by PayPal')),
                ('checks_accepted', models.BooleanField(default=True)),
                ('check_cost_increase', models.IntegerField(help_text=b'amount to be added to paypal_cost if paying by check')),
                ('late_cost_increase', models.IntegerField(help_text=b'amount to be added to paypal_cost if paying after price_increase_start_date')),
                ('mail_check_address', models.TextField(help_text=b'treasurer mailing address')),
                ('coupons_accepted', models.BooleanField(default=True)),
                ('division_email', models.CharField(help_text=b'email address for just this league', max_length=64, null=True, blank=True)),
                ('division_email_group_id', models.CharField(max_length=128, null=True, blank=True)),
                ('division_captains_email', models.CharField(help_text=b'email address for league captains', max_length=64, null=True, blank=True)),
                ('division_captains_email_group_id', models.CharField(max_length=128, null=True, blank=True)),
                ('state', models.CharField(help_text=b'state of league, changes whether registration is open or league is visible', max_length=32, choices=[(b'closed', b'Closed - visible to all, registration closed to all'), (b'hidden', b'Hidden - hidden to all, registration closed to all'), (b'open', b'Open - visible to all, registration conditionally open to all'), (b'preview', b'Preview - visible only to admins, registration conditionally open only to admins')])),
                ('image_cover', models.ImageField(null=True, upload_to=ultimate.leagues.models.generateLeagueCoverImagePath, blank=True)),
            ],
            options={
                'ordering': ['-year', '-season__order', 'league_start_date'],
                'db_table': 'league',
            },
        ),
        migrations.CreateModel(
            name='LeagueFields',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'field_league',
                'verbose_name_plural': 'league fields',
            },
        ),
        migrations.CreateModel(
            name='Registrations',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('registered', models.DateTimeField(default=None, null=True, blank=True)),
                ('conduct_complete', models.BooleanField(default=False)),
                ('waiver_complete', models.BooleanField(default=False)),
                ('pay_type', models.CharField(blank=True, max_length=6, null=True, choices=[(b'check', b'Check'), (b'paypal', b'PayPal')])),
                ('paypal_invoice_id', models.CharField(max_length=127, null=True, blank=True)),
                ('paypal_complete', models.BooleanField(default=False)),
                ('check_complete', models.BooleanField(default=False)),
                ('payment_complete', models.BooleanField(default=False)),
                ('refunded', models.BooleanField(default=False)),
                ('waitlist', models.BooleanField(default=False)),
                ('attendance', models.IntegerField(null=True, blank=True)),
                ('captain', models.IntegerField(blank=True, null=True, choices=[(0, 'I refuse to captain.'), (1, 'I will captain if absolutely necessary.'), (2, 'I am willing to captain.'), (3, 'I would like to captain.'), (4, "I will be very sad if I don't get to captain.")])),
            ],
            options={
                'db_table': 'registrations',
                'verbose_name_plural': 'registrations',
            },
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('slug', models.SlugField()),
                ('order', models.IntegerField(default=None, null=True)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, blank=True)),
                ('color', models.CharField(max_length=96, blank=True)),
                ('email', models.CharField(max_length=128, blank=True)),
                ('hidden', models.BooleanField(default=False)),
                ('group_id', models.CharField(max_length=128, null=True, blank=True)),
            ],
            options={
                'db_table': 'team',
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('captain', models.BooleanField(default=False)),
                ('team', models.ForeignKey(to='leagues.Team')),
            ],
            options={
                'ordering': ['-captain', 'user__last_name'],
                'db_table': 'team_member',
            },
        ),
    ]
