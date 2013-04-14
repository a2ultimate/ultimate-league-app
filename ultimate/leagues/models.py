from django import forms
from django.db import models, transaction
from django.db.models import Count
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from pybb.models import *

from datetime import date, datetime
import re

class Field(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.TextField()
	layout_link = models.TextField()
	address = models.TextField()
	driving_link = models.TextField()
	note = models.TextField()
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
		ordering = ['field__name', 'name']

	def __unicode__(self):
		return '%s %s' % (self.field.name, self.name)

LEAGUE_STATE_CHOICES = (
	('archived', 'Archived'),
	('planning', 'Planning'),
	('active', 'Active'),
	)

LEAGUE_GENDER_CHOICES = (
	('coed',        'Normal co-ed gender matched'),
	('50/50',       '50/50 league'),
	('hat',         'Hat tourney'),
	('hat_free',    'Hat tourney (no pay, just add to registration list)'),
	('hat_nocap',   'Hat tourney (no captains)'),
	('bonanza_free','Clinics and pickup (no pay)'),
	('competitive', 'Competitve league'),
	('showcase',    'Showcase league'),
	('party',       'No group-limits party night'),
	('open',        'Open, no gender match'),
	('women',       'Women only'),
	)

class League(models.Model):
	id = models.AutoField(primary_key=True)
	night = models.CharField(max_length=96, help_text='lower case, no special characters, e.g. "sunday", "tuesday and thursday", "end of season tournament"')
	season = models.CharField(max_length=96, help_text='lower case, no special characters, e.g. "late fall", "winter"')
	year = models.IntegerField(help_text='four digit year, e.g. 2013')
	gender = models.CharField(max_length=96, choices=LEAGUE_GENDER_CHOICES)
	gender_note = models.TextField(help_text='gender or other notes for league, e.g. 50/50 league, showcase league notes')
	baggage = models.IntegerField(help_text='max baggage group size')
	times = models.TextField(help_text='start to end time, e.g. 6:00-8:00pm')
	reg_start_date = models.DateField(help_text='date that registration process is open (not currently automated)')
	waitlist_start_date = models.DateField(help_text='date that waitlist is started (regardless of number of registrations)')
	freeze_group_date = models.DateField(help_text='date of last day to form groups')
	league_start_date = models.DateField(help_text='date of first game')
	league_end_date = models.DateField(help_text='date of last game')
	paypal_cost = models.IntegerField()
	check_cost = models.IntegerField()
	max_players = models.IntegerField(help_text='max players for league, extra registrations will be placed on waitlist')
	state = models.CharField(max_length=96, choices=LEAGUE_STATE_CHOICES, help_text='''
		Archived - not visible to anyone<br/>
		Planning - only visibil to junta<br/>
		Active - visible to everyone''')
	field = models.ManyToManyField(Field, db_table='field_league', help_text='''Select the fields these games will be played at, use
		the green "+" icon if we're playing at a new field.''')
	details = models.TextField(help_text='details page text, use HTML')
	league_email = models.CharField(max_length=192, blank=True, help_text='email address for entire season')
	league_captains_email = models.CharField(max_length=192, blank=True, help_text='email address for league captains')
	division_email = models.CharField(max_length=192, blank=True, help_text='email address for just this league')
	mail_check_address = models.TextField(help_text='treasurer mailing address')

	class Meta:
		db_table = u'league'

	def get_fields(self):
		return self.fieldleague_set.all()

	def get_field_names(self):
		return FieldNames.objects.filter(field__fieldleague__league=self, game__schedule__league=self).distinct().order_by('field__name', 'name')

	def get_league_registrations_for_user(self, user):
		return self.registrations_set.filter(user=user)

	def get_registrations(self):
		return Registrations.objects.filter(league=self).order_by('registered')

	def get_completed_registrations(self):
		registrations = Registrations.objects.filter(league=self).order_by('registered')
		return [r for r in registrations if not r.waitlist and not r.refunded and r.is_complete()]

	def get_waitlisted_registrations(self):
		registrations = Registrations.objects.filter(league=self).order_by('registered')
		return [r for r in registrations if r.waitlist and not r.refunded and r.is_complete()]

	def get_user_games(self, user):
		return self.schedule_set.all()[0].get_games().filter(gameteams__team__teammember__user=user).order_by('date')

	def get_num_game_events(self):
		try:
			return self.schedule_set.all()[0].get_games().count() / (self.team_set.all().count() / 2)
		except:
			return 0

	def get_league_captains(self):
		return User.objects.filter(teammember__team__league=self, teammember__captain=1)

	def get_league_captains_teammember(self):
		return TeamMember.objects.filter(team__league=self, captain=1).order_by('team')

	def player_survey_complete_for_user(self, user):
		return bool(self.team_set.filter(teammember__user=user)[0].player_survey_complete(user))

	@property
	def is_accepting_registrations(self):
		return self.state == 'active' and self.league_end_date > date.today()

	@property
	def is_accepting_waitlist(self):
		return self.state == 'active' and date.today() >= self.waitlist_start_date

	def __unicode__(self):
		return '%s %d %s' % (self.season, self.year, self.night)


class FieldLeague(models.Model):
	id = models.AutoField(primary_key=True)
	league = models.ForeignKey('leagues.League')
	field = models.ForeignKey('leagues.Field')

	class Meta:
		db_table = u'field_league'


class Schedule(models.Model):
	id = models.AutoField(primary_key=True)
	league = models.ForeignKey('leagues.League')

	class Meta:
		db_table = u'schedule'

	def get_games(self):
		return self.game_set.all().order_by('field_name__field__name', 'field_name__name')

	def score_report(self):
		return '<a href="%d/score_report/">View score reports</a>' % self.id
	score_report.allow_tags = True

	def __unicode__(self):
		return '%d %s %s' % (self.league.year,
			self.league.season.title(),
			self.league.night.title())


GENDER_CHOICES = (
	('M', 'Male'),
	('F', 'Female'),
)


class Player(PybbProfile):
	user = models.ForeignKey(User, db_column='id')
	groups = models.TextField()
	nickname = models.CharField(max_length=90)
	phone = models.CharField(max_length=45)
	street_address = models.CharField(max_length=765)
	city = models.CharField(max_length=127)
	state = models.CharField(max_length=6)
	zipcode = models.CharField(max_length=15)
	gender = models.CharField(max_length=3, choices=GENDER_CHOICES)
	height_inches = models.IntegerField()
	highest_level = models.TextField()
	birthdate = models.DateField()
	jersey_size = models.CharField(max_length=45)

	class Meta:
		db_table = u'player'

	def get_spirit(self):
		return self.user.skills.exclude(spirit=0)


class Baggage(models.Model):
	id = models.AutoField(primary_key=True)

	class Meta:
		db_table = u'baggage'

	def get_registrations(self):
		return self.registrations_set.all()

	@property
	def num_registrations(self):
		return self.registrations_set.all().count()

REGISTRATION_STATUS_CHOICES=(
	('new', 'New'),
	('refunded', 'Refunded'),
	('reversed', 'Reversed'),
	('clicked_waiver', 'Clicked Waiver'),
	('check_pending', 'Check Pending'),
	('clicked_insurance', 'Clicked Insurance'),
	('check_completed', 'Check Completed'),
	('paypal_pending', 'Paypal Pending'),
	('paypal_completed', 'Paypal Completed'),
	('paypal-pending_waitlist', 'Paypal Pending Waitlist'),
	('paypal-completed_waitlist', 'Paypal Completed Waitlist'),
	('paypal-canceled_reversal', 'Paypal Canceled Reversal'),
	('paypal-denied', 'Paypal Denied'),
	('check-completed_waitlist', 'Check Completed Waitlist'),
)

GOOD_REGISTRATION_STATUS_CHOICES=[
	'check_completed',
	'paypal_pending',
	'paypal_completed',
]

WAITLIST_REGISTRATION_STATUS_CHOICES=[
	'paypal-pending_waitlist',
	'paypal-completed_waitlist',
	'check-completed_waitlist',
]

BAD_REGISTRATION_STATUS_CHOICES=[
	'new',
	'refunded',
	'reversed',
	'clicked_waiver',
	'check_pending',
	'clicked_insurance',
	'paypal-denied',
	'paypal-canceled_reversal',
]


class Registration(models.Model):
	id = models.AutoField(primary_key=True)
	league = models.ForeignKey('leagues.League')
	status = models.TextField(choices=REGISTRATION_STATUS_CHOICES)
	user = models.ForeignKey(User)
	captaining = models.IntegerField()
	baggage = models.ForeignKey('leagues.Baggage')
	reg_time = models.DateTimeField()
	attendance = models.IntegerField()

	class Meta:
		db_table = u'registration'

	def __unicode__(self):
		return '%d %s %s - %s %s' % (self.league.year, self.league.season, self.league.night, self.status, self.user)

REGISTRATION_PAYMENT_CHOICES=[
	('check', 'check'),
	('paypal', 'paypal')
]


class Registrations(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User)
	league = models.ForeignKey('leagues.League')
	baggage = models.ForeignKey('leagues.Baggage', null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	registered = models.DateTimeField()
	conduct_complete = models.BooleanField()
	waiver_complete = models.BooleanField()
	pay_type = models.TextField(choices=REGISTRATION_PAYMENT_CHOICES, null=True)
	check_complete = models.BooleanField()
	paypal_invoice_id = models.CharField(max_length=127)
	paypal_complete = models.BooleanField()
	refunded = models.BooleanField()
	waitlist = models.BooleanField()
	attendance = models.IntegerField(null=True, blank=True)
	captain = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = u'registrations'

	def get_status(self):
		status = 'New'
		if self.refunded:
			status = 'Refunded'
		elif self.conduct_complete:
			status = 'Conduct Completed'
			if self.waiver_complete:
				status = 'Waiver Completed'
				if self.attendance != None and self.captain != None:
					status = 'Attendance Completed'

					if self.pay_type == 'check' and not self.check_complete:
						status = 'Waiting for Check'
					elif self.pay_type == 'check' and self.check_complete:
						status = 'Check Completed'
					elif self.pay_type == 'paypal' and not self.paypal_complete:
						status = 'Waiting for Paypal'
					elif self.pay_type == 'paypal' and self.paypal_complete:
						status = 'Paypal Completed'
		return status

	def get_progress(self):
		percentage = 0
		if self.conduct_complete:
			percentage = 20
			if self.waiver_complete:
				percentage = 40
				if self.attendance != None and self.captain != None:
					percentage = 60
					if self.pay_type:
						percentage = 80
						if self.check_complete or self.paypal_complete:
							percentage = 100
		return percentage

	def is_complete(self):
		return bool(self.conduct_complete and self.waiver_complete and self.attendance != None and self.captain != None and self.pay_type and (self.check_complete or self.paypal_complete)) and not self.refunded

	@transaction.commit_on_success
	def add_to_baggage_group(self, email):
		if self.waitlist:
			return 'You are currently on the waitlist and are ineligible to form baggage groups.'

		try:
			registration = Registrations.objects.get(user__email=email, league=self.league)
		except ObjectDoesNotExist:
			return 'No registration found for ' + email + '.'

		if registration.waitlist:
			return email + ' is currently on the waitlist and is ineligible to form baggage groups.'

		baggage_limit = self.league.baggage

		current_baggage = self.baggage
		current_baggage_registrations = current_baggage.get_registrations()

		target_baggage = registration.baggage

		if (current_baggage_registrations.count() + target_baggage.num_registrations > baggage_limit):
			return 'Baggage group with ' + email + ' exceeds limit.'

		for current_baggage_registration in current_baggage_registrations:
			current_baggage_registration.baggage = target_baggage
			current_baggage_registration.save()

		current_baggage.delete()

		return True


	@transaction.commit_manually
	def leave_baggage_group(self):
		try:
			baggage = Baggage()
			baggage.save()

			if (self.baggage.get_registrations().count() <= 1):
				self.baggage.delete()

			self.baggage = baggage
			self.save()

		except:
			transaction.rollback()
			return False
		else:
			transaction.commit()

		return True


	def __unicode__(self):
		return '%d %s %s - %s %s' % (self.league.year, self.league.season, self.league.night, self.user)


class Team(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	color = models.CharField(max_length=96)
	email = models.TextField()
	league = models.ForeignKey('leagues.League')

	class Meta:
		db_table = u'team'

	@property
	def size(self):
		return self.teammember_set.all().count()

	@property
	def css_background_color(self):
		if (re.search(r'black', self.color, re.I)):
			return '#2C3E50'
		if (re.search(r'blue', self.color, re.I)):
			return '#3498DB'
		if (re.search(r'green', self.color, re.I)):
			return '#2ECC71'
		if (re.search(r'orange', self.color, re.I)):
			return '#E67E22'
		if (re.search(r'pink', self.color, re.I)):
			return '#EE6FA0'
		if (re.search(r'red', self.color, re.I)):
			return '#E74C3C'
		if (re.search(r'white', self.color, re.I)):
			return '#FFFFFF'
		if (re.search(r'yellow', self.color, re.I)):
			return '#F1C40F'
		return '#95A5A6'

	@property
	def css_text_color(self):
		if (re.search(r'white', self.color, re.I)):
			return '#2C3E50'
		return '#FFFFFF'

	def get_members(self):
		return self.teammember_set.all()

	def on_team(self, user):
		return bool(self.teammember_set.filter(user=user))

	def player_survey_complete(self, user):
		skill_reports = self.skillsreport_set.annotate(num_skills=Count('skills')).filter(submitted_by=user)
		# since you don't rate yourself, looking for a skill report and teamsize - 1 skill entries
		return bool(skill_reports.count() > 0) and \
			bool(skill_reports.filter(num_skills__gte=self.size - 1).count() > 0)


class TeamMember(models.Model):
	id = models.AutoField(primary_key=True)
	team = models.ForeignKey('leagues.Team')
	user = models.ForeignKey(User)
	captain = models.IntegerField()

	class Meta:
		db_table = u'team_member'
		ordering = ['-captain', 'user__last_name']


class Game(models.Model):
	id = models.AutoField(primary_key=True)
	date = models.DateField()
	field_name = models.ForeignKey('leagues.FieldNames')
	schedule = models.ForeignKey('leagues.Schedule')

	class Meta:
		db_table = u'game'
		ordering = ['date', 'field_name']

	def get_teams(self):
		return Team.objects.filter(gameteams__game=self).all()

	def get_user_team(self, user):
		return self.gameteams_set.filter(team__teammember__user=user)[0:1].get().team

	def get_user_opponent(self, user):
		return self.gameteams_set.exclude(team__teammember__user=user)[0:1].get().team

	def get_reports(self):
		return self.gamereport_set.all()

	def report_complete_for_team(self, user):
		for report in self.gamereport_set.filter(team__teammember__user=user, team__teammember__captain=1):
			if (report.is_complete):
				return True
		return False

	def report_complete_for_user(self, user):
		for report in self.gamereport_set.filter(last_updated_by=user, team__teammember__user=user, team__teammember__captain=1):
			if (report.is_complete):
				return report.game.id
		return False


class GameTeams(models.Model):
	id = models.AutoField(primary_key=True)
	game = models.ForeignKey('leagues.Game')
	team = models.ForeignKey('leagues.Team')

	class Meta:
		db_table = u'game_teams'

SKILL_CHOICES=[
	0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
]


class SkillsType(models.Model):
	id = models.AutoField(primary_key=True)
	description = models.TextField()
	weight = models.FloatField()

	class Meta:
		db_table = u'skills_type'


class SkillsReport(models.Model):
	id = models.AutoField(primary_key=True)
	submitted_by = models.ForeignKey(User, related_name='skills_report_submitted_by_set')
	team = models.ForeignKey('leagues.Team')
	updated = models.DateTimeField()

	class Meta:
		db_table = u'skills_report'


class Skills(models.Model):
	id = models.AutoField(primary_key=True)
	skills_report = models.ForeignKey('leagues.SkillsReport')
	highest_level = models.TextField()
	athletic = models.PositiveIntegerField(default=0)
	experience = models.PositiveIntegerField(default=0)
	forehand = models.PositiveIntegerField(default=0)
	backhand = models.PositiveIntegerField(default=0)
	receive = models.PositiveIntegerField(default=0)
	handle = models.PositiveIntegerField(default=0)
	strategy = models.PositiveIntegerField(default=0)
	skills_type = models.ForeignKey('leagues.SkillsType')
	user = models.ForeignKey(User)
	submitted_by = models.ForeignKey(User, related_name='skills_submitted_by_set')
	updated = models.DateField()
	spirit = models.PositiveIntegerField(default=0)
	not_sure = models.BooleanField()

	class Meta:
		db_table = u'skills'
