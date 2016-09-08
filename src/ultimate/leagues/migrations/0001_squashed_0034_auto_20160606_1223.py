# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [(b'leagues', '0001_initial'), (b'leagues', '0002_auto_20151018_2201'), (b'leagues', '0003_auto_20151018_2204'), (b'leagues', '0004_auto_20151105_2210'), (b'leagues', '0005_auto_20160126_2148'), (b'leagues', '0006_auto_20160126_2205'), (b'leagues', '0007_auto_20160126_2205'), (b'leagues', '0008_auto_20160126_2228'), (b'leagues', '0009_auto_20160126_2228'), (b'leagues', '0010_auto_20160202_2257'), (b'leagues', '0011_auto_20160215_2008'), (b'leagues', '0012_auto_20160215_2025'), (b'leagues', '0013_auto_20160224_2235'), (b'leagues', '0014_auto_20160227_1825'), (b'leagues', '0015_auto_20160227_1827'), (b'leagues', '0016_game_start'), (b'leagues', '0017_auto_20160309_2110'), (b'leagues', '0018_auto_20160309_2113'), (b'leagues', '0019_auto_20160309_2117'), (b'leagues', '0020_auto_20160326_1954'), (b'leagues', '0021_auto_20160326_1955'), (b'leagues', '0022_auto_20160327_1916'), (b'leagues', '0022_auto_20160519_1150'), (b'leagues', '0023_coupon'), (b'leagues', '0024_auto_20160327_2226'), (b'leagues', '0025_auto_20160327_2226'), (b'leagues', '0026_coupon_use_count'), (b'leagues', '0027_registrations_coupon'), (b'leagues', '0028_league_coupons_accepted'), (b'leagues', '0029_auto_20160410_1807'), (b'leagues', '0030_registrations_payment_complete'), (b'leagues', '0031_auto_20160410_2056'), (b'leagues', '0032_auto_20160519_1224'), (b'leagues', '0033_auto_20160604_1231'), (b'leagues', '0034_auto_20160606_1223')]

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
                ('field', models.ManyToManyField(help_text=b'Select the fields these games will be played at, use the green "+" icon if we\'re playing at a new field.', to=b'leagues.Field', through='leagues.FieldLeague')),
            ],
            options={
                'db_table': 'league',
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
        migrations.AlterField(
            model_name='league',
            name='gender',
            field=models.CharField(max_length=32, choices=[(b'50/50', b'50/50 League'), (b'co-ed', b'Normal Co-Ed Gender Matched'), (b'competitive', b'Competitive League'), (b'event', b'Special Event'), (b'hat', b'Hat Tourney'), (b'open', b'Open, No Gender Match'), (b'showcase', b'Showcase League'), (b'women', b'Women Only')]),
        ),
        migrations.AddField(
            model_name='league',
            name='level',
            field=models.CharField(default='recreational', max_length=32, choices=[(b'competitive', b'Competitive'), (b'recreational', b'Recreational')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='league',
            name='type',
            field=models.CharField(default='league', max_length=32, choices=[(b'event', b'Event'), (b'league', b'League'), (b'tournament', b'Tournament')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='league',
            name='gender',
            field=models.CharField(max_length=32, choices=[(b'50/50', b'50/50 League'), (b'coed', b'Normal Co-Ed Gender Matched'), (b'competitive', b'Competitive League'), (b'event', b'Special Event'), (b'hat', b'Hat Tourney'), (b'open', b'Open, No Gender Match'), (b'showcase', b'Showcase League'), (b'women', b'Women Only'), (b'mens', b"Men's"), (b'mixed', b'Mixed'), (b'open', b'Open'), (b'womens', b"Women's")]),
        ),
        migrations.AlterField(
            model_name='league',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
        ),
        migrations.RenameField(
            model_name='league',
            old_name='details',
            new_name='detailed_info',
        ),
        migrations.AlterField(
            model_name='league',
            name='gender',
            field=models.CharField(max_length=32, choices=[(b'mens', b"Men's"), (b'mixed', b'Mixed'), (b'open', b'Open'), (b'womens', b"Women's")]),
        ),
        migrations.RenameField(
            model_name='league',
            old_name='gender_note',
            new_name='summary_info',
        ),
        migrations.AlterField(
            model_name='league',
            name='summary_info',
            field=models.TextField(help_text=b'notes for league, e.g. 50-50 league format, showcase league notes'),
        ),
        migrations.AlterField(
            model_name='league',
            name='state',
            field=models.CharField(help_text=b'state of league, changes whether registration is open or league is visible', max_length=32, choices=[(b'CLOSED', b'Closed - visible to all, registration closed to all'), (b'HIDDEN', b'Hidden - hidden to all, registration closed to all'), (b'OPEN', b'Open - visible to all, registration conditionally open to all'), (b'PREVIEW', b'Preview - visible only to admins, registration conditionally open only to admins')]),
        ),
        migrations.AlterField(
            model_name='league',
            name='state',
            field=models.CharField(help_text=b'state of league, changes whether registration is open or league is visible', max_length=32, choices=[(b'closed', b'Closed - visible to all, registration closed to all'), (b'hidden', b'Hidden - hidden to all, registration closed to all'), (b'open', b'Open - visible to all, registration conditionally open to all'), (b'preview', b'Preview - visible only to admins, registration conditionally open only to admins')]),
        ),
        migrations.AddField(
            model_name='team',
            name='group_id',
            field=models.CharField(max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='league',
            name='state',
            field=models.CharField(help_text=b'state of league, changes whether registration is open or league is visible', max_length=32, choices=[(b'closed', b'Closed - visible to all, registration closed to all'), (b'hidden', b'Hidden - hidden to all, registration closed to all'), (b'open', b'Open - visible to all, registration conditionally open to all'), (b'preview', b'Preview - visible only to admins, registration conditionally open only to admins')]),
        ),
        migrations.AddField(
            model_name='league',
            name='end_time',
            field=models.TimeField(help_text=b'end time for league', null=True),
        ),
        migrations.AddField(
            model_name='league',
            name='num_time_slots',
            field=models.IntegerField(default=1, help_text=b'number of time slots'),
        ),
        migrations.AddField(
            model_name='league',
            name='start_time',
            field=models.TimeField(help_text=b'start time for league', null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='start',
            field=models.DateTimeField(null=True),
        ),
        migrations.RemoveField(
            model_name='league',
            name='league_captains_email',
        ),
        migrations.RemoveField(
            model_name='league',
            name='league_email',
        ),
        migrations.AddField(
            model_name='league',
            name='division_captains_email',
            field=models.CharField(help_text=b'email address for league captains', max_length=64, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='league',
            name='division_email',
            field=models.CharField(help_text=b'email address for just this league', max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='league',
            name='division_captains_email_group_id',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='league',
            name='division_email_group_id',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='league',
            name='schedule_note',
            field=models.TextField(help_text=b'note to appear under the schedule', blank=True),
        ),
        migrations.AlterField(
            model_name='registrations',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='registrations',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(help_text=b'Leaving this field empty will generate a random code.', unique=True, max_length=30, blank=True)),
                ('type', models.CharField(max_length=20, choices=[(b'full', b'Full Value'), (b'percentage', b'Percentage'), (b'amount', b'Amount')])),
                ('use_limit', models.IntegerField(default=1)),
                ('value', models.IntegerField(default=None, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('redeemed_at', models.DateTimeField(null=True, blank=True)),
                ('valid_until', models.DateTimeField(help_text=b'Leave empty for coupons that never expire', null=True, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('use_count', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'coupons',
            },
        ),
        migrations.AddField(
            model_name='registrations',
            name='coupon',
            field=models.ForeignKey(blank=True, to='leagues.Coupon', null=True),
        ),
        migrations.AddField(
            model_name='league',
            name='coupons_accepted',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='registrations',
            name='payment_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name='coupon',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='registrations',
            name='registered',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='league',
            name='level',
            field=models.CharField(max_length=32, choices=[(b'competitive', b'Competitive'), (b'recreational', b'Recreational'), (b'youth', b'Youth')]),
        ),
        migrations.AlterField(
            model_name='league',
            name='level',
            field=models.CharField(max_length=32, choices=[(b'comp', b'Competitive'), (b'rec', b'Recreational'), (b'youth', b'Youth')]),
        ),
        migrations.RunSQL(
            sql='UPDATE league SET level = "comp" WHERE level = "competitive";',
        ),
        migrations.RunSQL(
            sql='UPDATE league SET level = "rec" WHERE level = "recreational";',
        ),
    ]
