from datetime import date, datetime

from django.db import models
from django.db.models import Count
from django.db.transaction import atomic
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from pybb.models import *



class Field(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.TextField()
	layout_link = models.TextField(blank=True)
	address = models.TextField(blank=True)
	driving_link = models.TextField(blank=True)
	note = models.TextField(blank=True)

	class Meta:
		db_table = u'field'
		ordering = ['name']

	def __unicode__(self):
		return self.name


class FieldNames(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.TextField()
	field = models.ForeignKey('leagues.Field')

	class Meta:
		db_table = u'field_names'
		verbose_name_plural = 'field names'
		ordering = ['field__name', 'name']

	def __unicode__(self):
		return '%s %s' % (self.field.name, self.name)


class League(models.Model):
	STATE_CLOSED = 'closed'
	STATE_HIDDEN = 'hidden'
	STATE_OPEN = 'open'
	STATE_PREVIEW = 'preview'
	LEAGUE_STATE_CHOICES = (
		(STATE_CLOSED,	'Closed - visible to all, registration closed to all'),
		(STATE_HIDDEN,	'Hidden - hidden to all, registration closed to all'),
		(STATE_OPEN,	'Open - visible to all, registration conditionally open to all'),
		(STATE_PREVIEW,	'Preview - visible only to admins, registration conditionally open only to admins'),
	)

	LEAGUE_GENDER_CHOICES = (
		('mens',		'Men\'s'),
		('mixed',		'Mixed'),
		('open',		'Open'),
		('womens',		'Women\'s'),
	)

	LEAGUE_LEVEL_CHOICES = (
		('competitive', 'Competitive'),
		('recreational', 'Recreational'),
	)

	LEAGUE_TYPE_CHOICES = (
		('event', 'Event'),
		('league', 'League'),
		('tournament', 'Tournament'),
	)

	night = models.CharField(max_length=32, help_text='lower case, no special characters, e.g. "sunday", "tuesday and thursday", "end of season tournament"')
	season = models.CharField(max_length=32, help_text='lower case, no special characters, e.g. "late fall", "winter"')
	year = models.IntegerField(help_text='four digit year, e.g. 2013')

	gender = models.CharField(max_length=32, choices=LEAGUE_GENDER_CHOICES)
	level = models.CharField(max_length=32, choices=LEAGUE_LEVEL_CHOICES)
	type = models.CharField(max_length=32, choices=LEAGUE_TYPE_CHOICES)

	summary_info = models.TextField(help_text='notes for league, e.g. 50-50 league format, showcase league notes')
	detailed_info = models.TextField(help_text='details page text, use HTML')

	times = models.TextField(help_text='start to end time, e.g. 6:00-8:00pm')
	num_games_per_week = models.IntegerField(default=1, help_text='number of games per week, used to calculate number of games for a league')
	reg_start_date = models.DateTimeField(help_text='date and time that registration process is open (not currently automated)')
	price_increase_start_date = models.DateTimeField(help_text='date and time when cost increases for league')
	waitlist_start_date = models.DateTimeField(help_text='date and time that waitlist is started (regardless of number of registrations)')
	league_start_date = models.DateField(help_text='date of first game')
	league_end_date = models.DateField(help_text='date of last game')

	max_players = models.IntegerField(help_text='max players for league, extra registrations will be placed on waitlist')
	baggage = models.IntegerField(help_text='max baggage group size')

	paypal_cost = models.IntegerField(help_text='base cost of league if paying by PayPal')
	checks_accepted = models.BooleanField(default=True)
	check_cost_increase = models.IntegerField(help_text='amount to be added to paypal_cost if paying by check')
	late_cost_increase = models.IntegerField(help_text='amount to be added to paypal_cost if paying after price_increase_start_date')
	mail_check_address = models.TextField(help_text='treasurer mailing address')

	field = models.ManyToManyField(Field, through='FieldLeague', help_text='Select the fields these games will be played at, use the green "+" icon if we\'re playing at a new field.')

	league_email = models.CharField(max_length=64, blank=True, help_text='email address for entire season')
	league_captains_email = models.CharField(max_length=64, blank=True, help_text='email address for league captains')
	division_email = models.CharField(max_length=64, blank=True, help_text='email address for just this league')

	state = models.CharField(max_length=32, choices=LEAGUE_STATE_CHOICES, help_text='state of league, changes whether registration is open or league is visible')

	class Meta:
		db_table = u'league'

	@property
	def night_title(self):
		return ('%s' % (self.night)).replace('_', ' ')

	@property
	def season_title(self):
		return ('%s' % (self.season)).replace('_', ' ')

	@property
	def season_year(self):
		return ('%s %d' % (self.season, self.year)).replace('_', ' ')

	@property
	def gender_title(self):
		return ('%s' % (self.gender)).replace('_', ' ')

	@property
	def paypal_price(self):
		if self.paypal_cost == 0 or datetime.now() < self.price_increase_start_date:
			return self.paypal_cost

		return self.paypal_cost + self.late_cost_increase

	@property
	def check_price(self):
		if self.paypal_cost + self.check_cost_increase == 0 or datetime.now() < self.price_increase_start_date:
			return self.paypal_cost + self.check_cost_increase

		return self.paypal_cost + self.check_cost_increase + self.late_cost_increase

	def get_fields(self):
		return FieldLeague.objects.filter(league=self)

	def get_field_names(self):
		return FieldNames.objects.filter(field__fieldleague__league=self, game__league=self).distinct().order_by('field__name', 'name')

	def get_teams(self):
		return Team.objects.filter(league=self, hidden=False)

	def get_games(self):
		return Game.objects.filter(league=self).order_by('field_name__field__name', 'field_name__name', 'date')

	def get_user_games(self, user):
		return Game.objects.filter(league=self, gameteams__team__teammember__user=user).order_by('date')

	def get_num_game_events(self):
		diff = self.league_end_date - self.league_start_date
		num_weeks = (diff.days / 7) + 1

		if self.num_games_per_week > 1:
			num_games = num_weeks * self.num_games_per_week
		else:
			num_games = num_weeks

		return num_games

	def get_league_captains(self):
		return User.objects.filter(teammember__team__league=self, teammember__captain=1)

	def get_league_captains_teammember(self):
		return TeamMember.objects.filter(team__league=self, captain=1).order_by('team')

	def player_survey_complete_for_user(self, user):
		return bool(user.teammember_set.get(team__league=self).team.player_survey_complete(user))

	def get_registrations_for_user(self, user):
		return Registrations.objects.filter(league=self, user=user)

	def get_complete_registrations(self):
		registrations = Registrations.objects.filter(league=self).order_by('registered')
		return [r for r in registrations if r.is_complete and not r.waitlist and not r.refunded]

	def get_waitlist_registrations(self):
		registrations = Registrations.objects.filter(league=self).order_by('registered')
		return [r for r in registrations if r.is_complete and r.waitlist and not r.refunded]

	def get_incomplete_registrations(self):
		registrations = Registrations.objects.filter(league=self).order_by('registered')
		return [r for r in registrations if not r.is_complete and not r.refunded]

	def get_refunded_registrations(self):
		registrations = Registrations.objects.filter(league=self).order_by('registered')
		return [r for r in registrations if r.is_complete and r.refunded]

	def get_unassigned_registrations(self):
		team_member_users = [t.user for t in TeamMember.objects.filter(team__league=self)]
		registrations = Registrations.objects.filter(league=self).exclude(user__in=team_member_users)
		return [r for r in registrations if r.is_complete and not r.refunded]

	def is_visible(self, user=None):
		if user and (user.is_superuser or user.groups.filter(name='junta').exists()):
			return self.state in ['closed', 'open', 'preview']

		return self.state in ['closed', 'open']

	def is_open(self, user=None):
		# if the user is a league admin and the league is "open" or "preview"
		if user and \
			(user.is_superuser or user.groups.filter(name='junta').exists()) and \
			self.state in ['preview', 'open']:

			return True

		# if the user is not a league admin and the league is "open" and falls between valid dates
		return self.state in ['open'] and \
			(datetime.now() >= self.reg_start_date) and \
			(date.today() <= self.league_end_date)

	def is_waitlist(self, user=None):
		# if the league is open and its after the waitlist date or league is full
		return self.is_open(user) and \
			( \
				(datetime.now() >= self.waitlist_start_date) or \
				(len(self.get_complete_registrations()) >= self.max_players) \
			)

	@property
	def is_after_registration_start(self):
		return datetime.now() >= self.reg_start_date

	@property
	def is_after_price_increase(self):
		return datetime.now() >= self.price_increase_start_date

	def __unicode__(self):
		return ('%s %d %s' % (self.season, self.year, self.night)).replace('_', ' ')


class FieldLeague(models.Model):
	id = models.AutoField(primary_key=True)
	league = models.ForeignKey('leagues.League')
	field = models.ForeignKey('leagues.Field')

	class Meta:
		db_table = u'field_league'


class Player(PybbProfile):
	GENDER_CHOICES = (
		('M',	'Male'),
		('F',	'Female'),
	)

	JERSEY_SIZE_CHOICES = (
		('XS',	'XS - Extra Small'),
		('S',	'S - Small'),
		('M',	'M - Medium'),
		('L',	'L - Large'),
		('XL',	'XL -Extra Large'),
		('XXL',	'XXL - Extra Extra Large'),
	)

	user = models.OneToOneField(User, related_name='profile')
	groups = models.TextField()
	nickname = models.CharField(max_length=30)
	phone = models.CharField(max_length=15)
	zip_code = models.CharField(max_length=15)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
	height_inches = models.IntegerField(blank=True, null=True)
	highest_level = models.TextField(blank=True, null=True)
	date_of_birth = models.DateField(help_text='e.g. ' + date.today().strftime('%Y-%m-%d'))
	jersey_size = models.CharField(max_length=45, choices=JERSEY_SIZE_CHOICES)

	guardian_name = models.TextField(blank=True)
	guardian_phone = models.TextField(blank=True)

	class Meta:
		db_table = u'player'

	@property
	def age(self, now=None):
		if not self.date_of_birth:
			return 0

		if now is None:
			now = date.today()

		return (now.year - self.date_of_birth.year) - int((now.month, now.day) < (self.date_of_birth.month, self.date_of_birth.day))

	@property
	def is_complete_for_user(self):
		is_complete = bool(self.gender and self.date_of_birth)

		if is_complete and self.age < 18:
			is_complete = bool(is_complete and self.guardian_name and self.guardian_phone)

		return is_complete


class Baggage(models.Model):
	id = models.AutoField(primary_key=True)

	class Meta:
		db_table = u'baggage'

	@property
	def num_registrations(self):
		return self.registrations_set.all().count()

	def get_registrations(self):
		return self.registrations_set.all()

	def __unicode__(self):
		return '%d' % (self.id)


class Registrations(models.Model):
	REGISTRATION_PAYMENT_CHOICES = (
		('check',	'Check'),
		('paypal',	'PayPal'),
	)

	REGISTRATION_CAPTAIN_CHOICES = (
		(0, u'I refuse to captain.'),
		(1, u'I will captain if absolutely necessary.'),
		(2, u'I am willing to captain.'),
		(3, u'I would like to captain.'),
		(4, u'I will be very sad if I don\'t get to captain.'),
	)

	id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User)
	league = models.ForeignKey('leagues.League')
	baggage = models.ForeignKey('leagues.Baggage', null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	registered = models.DateTimeField(null=True, blank=True)
	conduct_complete = models.BooleanField(default=False)
	waiver_complete = models.BooleanField(default=False)
	pay_type = models.CharField(choices=REGISTRATION_PAYMENT_CHOICES, max_length=6, null=True, blank=True)
	check_complete = models.BooleanField(default=False)
	paypal_invoice_id = models.CharField(max_length=127, null=True, blank=True)
	paypal_complete = models.BooleanField(default=False)
	refunded = models.BooleanField(default=False)
	waitlist = models.BooleanField(default=False)
	attendance = models.IntegerField(null=True, blank=True)
	captain = models.IntegerField(null=True, blank=True, choices=REGISTRATION_CAPTAIN_CHOICES)

	class Meta:
		db_table = u'registrations'
		verbose_name_plural = 'registrations'
		unique_together = ('user', 'league',)

	@property
	def status(self):
		status = 'New'
		if self.refunded:
			status = 'Refunded'
		elif self.conduct_complete:
			status = 'Conduct Completed'
			if self.waiver_complete:
				status = 'Waiver Completed'
				if self.attendance != None and self.captain != None:
					status = 'Attendance Completed'

					if self.league.check_price == 0 and self.league.paypal_price == 0:
						status = 'Registration Completed'

					else:
						if self.pay_type == 'check' and not self.check_complete:
							status = 'Waiting for Check'
						elif self.pay_type == 'check' and self.check_complete:
							status = 'Check Completed'
						elif self.pay_type == 'paypal' and not self.paypal_complete:
							status = 'Waiting for Paypal'
						elif self.pay_type == 'paypal' and self.paypal_complete:
							status = 'Paypal Completed'
		return status

	@property
	def progress(self):
		percentage = 0
		interval = 20

		if (self.league.check_price == 0 and self.league.paypal_price == 0) or not self.league.checks_accepted:
			interval = 25

		if self.conduct_complete:
			percentage += interval
			if self.waiver_complete:
				percentage += interval
				if self.attendance != None and self.captain != None:
					percentage += interval

					if self.league.checks_accepted and \
						self.league.check_price == 0 and \
						self.league.paypal_price == 0 and \
						self.pay_type:

						percentage += interval

					if self.check_complete or self.paypal_complete:
						percentage += interval

		return percentage

	@property
	def is_complete(self):
		return bool(self.conduct_complete and \
			self.waiver_complete and \
			self.attendance != None and \
			self.captain != None and \
			((self.league.check_price == 0 and self.league.paypal_price == 0) or \
			(self.pay_type and (self.check_complete or self.paypal_complete))) and \
			not self.refunded)

	@property
	def baggage_size(self):
		if self.baggage:
			return self.baggage.num_registrations
		return 0

	@property
	def rating_adjusted(self):
		rating_total = self.user.rating_total
		num_events = self.league.get_num_game_events()
		absence_weight = rating_total / num_events

		return rating_total - ((self.attendance / 2) * absence_weight)

	@atomic
	def add_to_baggage_group(self, email):
		if datetime.now() > self.league.waitlist_start_date:
			return 'You may not edit a baggage group after the group change deadline (' + self.league.waitlist_start_date.strftime('%Y-%m-%d') + ').'

		if self.user.email == email:
			return 'You cannot form a baggage group with yourself.'

		if not self.is_complete:
			return 'Your registration is currently incomplete and is ineligible to form baggage groups.'

		if self.waitlist:
			return 'You are currently on the waitlist and are ineligible to form baggage groups.'

		try:
			registration = Registrations.objects.get(user__email=email, league=self.league)
		except ObjectDoesNotExist:
			return 'No registration found for ' + email + '.'

		if not registration.is_complete:
			return email + ' has an incomplete registration and is ineligible to form baggage groups.'

		if registration.waitlist:
			return email + ' is currently on the waitlist and is ineligible to form baggage groups.'

		baggage_limit = self.league.baggage

		current_baggage = self.baggage
		current_baggage_registrations = current_baggage.get_registrations()

		target_baggage = registration.baggage

		if target_baggage == current_baggage:
			return email + ' is already part of your baggage group.'

		if (current_baggage_registrations.count() + target_baggage.num_registrations) > baggage_limit:
			return 'Baggage group with ' + email + ' exceeds limit.'

		for current_baggage_registration in current_baggage_registrations:
			current_baggage_registration.baggage = target_baggage
			current_baggage_registration.save()

		current_baggage.delete()

		return True


	def leave_baggage_group(self):
		if datetime.now() > self.league.waitlist_start_date:
			return 'You may not edit a baggage group after the group change deadline (' + self.league.waitlist_start_date.strftime('%Y-%m-%d') + ').'


		try:
			with transaction.atomic():
				baggage = Baggage()
				baggage.save()

				if self.baggage.get_registrations().count() <= 1:
					self.baggage.delete()

				self.baggage = baggage
				self.save()

		except:
			return False

		return True

	def get_team_id(self):
		try:
			return self.user.teammember_set.get(team__league=self.league).team.id
		except ObjectDoesNotExist:
			return None

	def __unicode__(self):
		return '%d %s %s - %s %s' % (self.league.year, self.league.season, self.league.night, self.user, self.status)


class Team(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128, blank=True)
	color = models.CharField(max_length=96, blank=True)
	email = models.CharField(max_length=128, blank=True)
	league = models.ForeignKey('leagues.League')
	hidden = models.BooleanField(default=False)

	class Meta:
		db_table = u'team'

	@property
	def attendance_total(self):
		return sum(registration.attendance for registration in Registrations.objects.filter(league=self.league, user__id__in=self.teammember_set.all().values_list('user', flat=True)))

	@property
	def attendance_average(self):
		if self.size > 0:
			return self.attendance_total / float(self.size)

		return 0

	@property
	def rating_total(self):
		return sum(team_member.user.rating_total for team_member in self.teammember_set.all())

	@property
	def rating_average(self):
		if self.size > 0:
			return self.rating_total / float(self.size)

		return 0

	@property
	def rating_total_adjusted(self):
		return sum(registration.rating_adjusted for registration in Registrations.objects.filter(league=self.league, user__id__in=self.teammember_set.all().values_list('user', flat=True)))

	@property
	def rating_average_adjusted(self):
		if self.size > 0:
			return self.rating_total_adjusted / float(self.size)

		return 0

	@property
	def size(self):
		return self.teammember_set.all().count()

	@property
	def css_background_color(self):
		color = '#95A5A6'
		if 'black' in self.color.lower():
			color = '#2C3E50'
		if 'blue' in self.color.lower():
			color = '#3498DB'
		if 'green' in self.color.lower():
			color = '#2ECC71'
		if 'orange' in self.color.lower():
			color = '#E67E22'
		if 'pink' in self.color.lower():
			color = '#EE6FA0'
		if 'purple' in self.color.lower():
			color = '#9B59B6'
		if 'red' in self.color.lower():
			color = '#E74C3C'
		if 'yellow' in self.color.lower():
			color = '#F1C40F'
		if 'white' in self.color.lower():
			color = '#FFFFFF'
		return color

	@property
	def css_text_color(self):
		color = '#FFFFFF'
		if 'white' in self.color.lower():
			color = '#2C3E50'
		return color

	def contains_user(self, user):
		return bool(self.teammember_set.filter(user=user))

	def get_captains(self):
		return self.teammember_set.filter(captain=True)

	def get_members(self):
		return self.teammember_set.all()

	def get_members_with_baggage(self):
		return self.teammember_set.extra(select={'baggage_id':'SELECT baggage_id FROM registrations JOIN team ON team.league_id = registrations.league_id WHERE registrations.user_id = team_member.user_id AND team.id = team_member.team_id'}).order_by('baggage_id')

	def get_male_members(self):
		return TeamMember.objects.filter(team=self, user__profile__gender__iexact='M')

	def get_female_members(self):
		return TeamMember.objects.filter(team=self, user__profile__gender__iexact='F')

	def get_games(self):
		return Game.objects.filter(gameteams__team=self)

	def get_past_games(self):
		return self.get_games().filter(date__lte=date.today())

	def get_record_list(self):
		# return in format {wins, losses, ties, conflicts}
		team_record = {'wins': 0, 'losses': 0, 'ties': 0, 'conflicts': 0, 'blanks': 0, 'points_for': 0, 'points_against': 0}

		games = self.get_games()
		for game in games:

			team_reports = game.gamereport_set.filter(team=self)
			opponent_reports = game.gamereport_set.exclude(team=self)
			points_for = float(0)
			points_against = float(0)
			report_count = float(team_reports.count() + opponent_reports.count())

			team_result = 0
			for report in team_reports:
				team_score = report.gamereportscore_set.filter(team=self)[0].score
				opponent_score = report.gamereportscore_set.exclude(team=self)[0].score

				points_for += team_score
				points_against += opponent_score

				if team_score > opponent_score:
					# team win
					team_result = 1
				elif team_score < opponent_score:
					# team loss
					team_result = 2
				else:
					# tie
					team_result = 3

			opponent_result = 0
			for report in opponent_reports:
				team_score = report.gamereportscore_set.filter(team=self)[0].score
				opponent_score = report.gamereportscore_set.exclude(team=self)[0].score

				points_for += team_score
				points_against += opponent_score

				if team_score > opponent_score:
					# win
					opponent_result = 1
				elif team_score < opponent_score:
					# loss
					opponent_result = 2
				else:
					# tie
					opponent_result = 3

			if (team_result == 1 and opponent_result == 1) or \
				(team_result == 1 and opponent_result == 0) or \
				(opponent_result == 1 and team_result == 0):

				team_record['wins'] += 1

			elif (team_result == 2 and opponent_result == 2) or \
				(team_result == 2 and opponent_result == 0) or \
				(opponent_result == 2 and team_result == 0):

				team_record['losses'] += 1

			elif (team_result == 3 and opponent_result == 3) or \
				(team_result == 3 and opponent_result == 0) or \
				(opponent_result == 3 and team_result == 0):

				team_record['ties'] += 1

			elif team_result != opponent_result and \
				team_result != 0 and \
				opponent_result != 0:

				team_record['conflicts'] += 1

			else:

				team_record['blanks'] += 1

			if report_count > 1:
				points_for /= report_count
				points_against /= report_count

			team_record['points_for'] += points_for
			team_record['points_against'] += points_against

		return team_record


	def player_survey_complete(self, user):
		ratings_reports = self.playerratingsreport_set.annotate(num_ratings=Count('playerratings')).filter(submitted_by=user)
		# since you don't rate yourself, looking for a rating report and teamsize - 1 rating entries
		return bool(ratings_reports.count() > 0) and \
			bool(ratings_reports.filter(num_ratings__gte=self.size - 1).count() > 0)

	def __unicode__(self):
		name = 'Team %d' % (self.id)

		if self.name:
			name = name + ' - ' + self.name
		if self.color:
			return name + (' (%s)' % (self.color))

		return name


class TeamMember(models.Model):
	id = models.AutoField(primary_key=True)
	team = models.ForeignKey('leagues.Team')
	user = models.ForeignKey(User)
	captain = models.BooleanField(default=False)

	class Meta:
		db_table = u'team_member'
		ordering = ['-captain', 'user__last_name']

	@property
	def attendance_total(self):
		return Registrations.objects.get(league=self.team.league, user=self.user).attendance

	def __unicode__(self):
		return '%s %s' % (self.user.first_name, self.user.last_name)


class Game(models.Model):
	id = models.AutoField(primary_key=True)
	date = models.DateField()
	field_name = models.ForeignKey('leagues.FieldNames')
	league = models.ForeignKey('leagues.league')

	class Meta:
		db_table = u'game'
		ordering = ['-date', 'field_name']

	def get_teams(self):
		return Team.objects.filter(gameteams__game=self, hidden=False)

	def get_user_opponent(self, user):
		try:
			return Team.objects.filter(gameteams__game=self, hidden=False).exclude(teammember__user=user)[0:1].get()
		except ObjectDoesNotExist:
			return None

	def get_report_for_team(self, team):
		return self.gamereport_set.filter(team=team)

	def report_complete_for_team(self, user):
		return any(report.is_complete for report in self.gamereport_set.filter(team__teammember__user=user, team__teammember__captain=1))

	def report_complete_for_user(self, user):
		return any(report.is_complete for report in self.gamereport_set.filter(last_updated_by=user, team__teammember__user=user, team__teammember__captain=1))

	def __unicode__(self):
		return '%s - %s' % (self.date, self.league)


class GameTeams(models.Model):
	id = models.AutoField(primary_key=True)
	game = models.ForeignKey('leagues.Game')
	team = models.ForeignKey('leagues.Team')

	class Meta:
		db_table = u'game_teams'
