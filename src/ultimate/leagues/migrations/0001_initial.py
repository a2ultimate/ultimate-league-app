# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
            name='Field',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('layout_link', models.TextField(blank=True)),
                ('address', models.TextField(blank=True)),
                ('driving_link', models.TextField(blank=True)),
                ('note', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'field',
            },
        ),
        migrations.CreateModel(
            name='FieldLeague',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('field', models.ForeignKey(to='leagues.Field')),
            ],
            options={
                'db_table': 'field_league',
            },
        ),
        migrations.CreateModel(
            name='FieldNames',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('field', models.ForeignKey(to='leagues.Field')),
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
                ('field_name', models.ForeignKey(to='leagues.FieldNames')),
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
                ('game', models.ForeignKey(to='leagues.Game')),
            ],
            options={
                'db_table': 'game_teams',
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('night', models.CharField(help_text=b'lower case, no special characters, e.g. "sunday", "tuesday and thursday", "end of season tournament"', max_length=32)),
                ('season', models.CharField(help_text=b'lower case, no special characters, e.g. "late fall", "winter"', max_length=32)),
                ('year', models.IntegerField(help_text=b'four digit year, e.g. 2013')),
                ('gender', models.CharField(max_length=32, choices=[(b'50/50', b'50/50 League'), (b'coed', b'Normal Co-Ed Gender Matched'), (b'competitive', b'Competitive League'), (b'event', b'Special Event'), (b'hat', b'Hat Tourney'), (b'open', b'Open, No Gender Match'), (b'showcase', b'Showcase League'), (b'women', b'Women Only')])),
                ('gender_note', models.TextField(help_text=b'gender or other notes for league, e.g. 50/50 league, showcase league notes')),
                ('baggage', models.IntegerField(help_text=b'max baggage group size')),
                ('times', models.TextField(help_text=b'start to end time, e.g. 6:00-8:00pm')),
                ('num_games_per_week', models.IntegerField(default=1, help_text=b'number of games per week, used to calculate number of games for a league')),
                ('reg_start_date', models.DateTimeField(help_text=b'date and time that registration process is open (not currently automated)')),
                ('price_increase_start_date', models.DateTimeField(help_text=b'date and time when cost increases for league')),
                ('waitlist_start_date', models.DateTimeField(help_text=b'date and time that waitlist is started (regardless of number of registrations)')),
                ('league_start_date', models.DateField(help_text=b'date of first game')),
                ('league_end_date', models.DateField(help_text=b'date of last game')),
                ('paypal_cost', models.IntegerField(help_text=b'base cost of league if paying by PayPal')),
                ('checks_accepted', models.BooleanField(default=True)),
                ('check_cost_increase', models.IntegerField(help_text=b'amount to be added to paypal_cost if paying by check')),
                ('late_cost_increase', models.IntegerField(help_text=b'amount to be added to paypal_cost if paying after price_increase_start_date')),
                ('max_players', models.IntegerField(help_text=b'max players for league, extra registrations will be placed on waitlist')),
                ('state', models.CharField(help_text=b'state of league, changes whether registration is open or league is visible', max_length=32, choices=[(b'closed', b'Closed - visible to all, registration closed to all'), (b'hidden', b'Hidden - hidden to all, registration closed to all'), (b'open', b'Open - visible to all, registration conditionally open to all'), (b'preview', b'Preview - visible only to admins, registration conditionally open only to admins')])),
                ('details', models.TextField(help_text=b'details page text, use HTML')),
                ('league_email', models.CharField(help_text=b'email address for entire season', max_length=64, blank=True)),
                ('league_captains_email', models.CharField(help_text=b'email address for league captains', max_length=64, blank=True)),
                ('division_email', models.CharField(help_text=b'email address for just this league', max_length=64, blank=True)),
                ('mail_check_address', models.TextField(help_text=b'treasurer mailing address')),
                ('field', models.ManyToManyField(help_text=b'Select the fields these games will be played at, use the green "+" icon if we\'re playing at a new field.', to='leagues.Field', through='leagues.FieldLeague')),
            ],
            options={
                'db_table': 'league',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_count', models.IntegerField(default=0, verbose_name='Post count', blank=True)),
                ('groups', models.TextField()),
                ('nickname', models.CharField(max_length=30)),
                ('phone', models.CharField(max_length=15)),
                ('street_address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=127)),
                ('state', models.CharField(max_length=6)),
                ('zipcode', models.CharField(max_length=15)),
                ('gender', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('height_inches', models.IntegerField()),
                ('highest_level', models.TextField()),
                ('birthdate', models.DateField(help_text=b'e.g. 2015-10-18')),
                ('jersey_size', models.CharField(max_length=45, choices=[(b'XS', b'XS - Extra Small'), (b'S', b'S - Small'), (b'M', b'M - Medium'), (b'L', b'L - Large'), (b'XL', b'XL -Extra Large'), (b'XXL', b'XXL - Extra Extra Large')])),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'player',
            },
        ),
        migrations.CreateModel(
            name='Registrations',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('registered', models.DateTimeField(null=True, blank=True)),
                ('conduct_complete', models.BooleanField(default=False)),
                ('waiver_complete', models.BooleanField(default=False)),
                ('pay_type', models.CharField(blank=True, max_length=6, null=True, choices=[(b'check', b'Check'), (b'paypal', b'PayPal')])),
                ('check_complete', models.BooleanField(default=False)),
                ('paypal_invoice_id', models.CharField(max_length=127, null=True, blank=True)),
                ('paypal_complete', models.BooleanField(default=False)),
                ('refunded', models.BooleanField(default=False)),
                ('waitlist', models.BooleanField(default=False)),
                ('attendance', models.IntegerField(null=True, blank=True)),
                ('captain', models.IntegerField(blank=True, null=True, choices=[(0, 'I refuse to captain.'), (1, 'I will captain if absolutely necessary.'), (2, 'I am willing to captain.'), (3, 'I would like to captain.'), (4, "I will be very sad if I don't get to captain.")])),
                ('baggage', models.ForeignKey(blank=True, to='leagues.Baggage', null=True)),
                ('league', models.ForeignKey(to='leagues.League')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'registrations',
                'verbose_name_plural': 'registrations',
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
                ('league', models.ForeignKey(to='leagues.League')),
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
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-captain', 'user__last_name'],
                'db_table': 'team_member',
            },
        ),
        migrations.AddField(
            model_name='gameteams',
            name='team',
            field=models.ForeignKey(to='leagues.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='league',
            field=models.ForeignKey(to='leagues.League'),
        ),
        migrations.AddField(
            model_name='fieldleague',
            name='league',
            field=models.ForeignKey(to='leagues.League'),
        ),
        migrations.AlterUniqueTogether(
            name='registrations',
            unique_together=set([('user', 'league')]),
        ),
    ]
