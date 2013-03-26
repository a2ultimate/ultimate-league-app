from django import forms
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User

from pybb.models import *

class Field(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.TextField()
	layout_link = models.TextField()
	address = models.TextField()
	driving_link = models.TextField()
	note = models.TextField()
	class Meta:
		db_table = u'field'

	def __unicode__(self):
		return self.name

class FieldNames(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.TextField()
	field = models.ForeignKey('leagues.Field')
	class Meta:
		db_table = u'field_names'

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
	('open',        'Open, can be coed, no gender match'),
	('women',       'Women only, no boys'),
	)

class League(models.Model):
	id = models.AutoField(primary_key=True)
	baggage = models.IntegerField(help_text='This is the max size for baggage groups')
	night = models.CharField(max_length=96, help_text='The league night (lowercase), spaces are okay here, but don\'t get too fancy with the !@_(#$^\'s')
	season = models.CharField(max_length=96, help_text='Season name (lowercase) - NO SPACES')
	year = models.IntegerField(help_text='Four digit year, i.e. 2008')
	gender = models.CharField(max_length=96, choices=LEAGUE_GENDER_CHOICES)
	gender_note = models.TextField(help_text='Summary text describing gender rules for this league, and anything else that should go on the league info page')
	times = models.TextField(help_text='Start end times, i.e. 6:00-8:00pm')
	reg_start_date = models.DateField(help_text='Day registration opens, although I\'m not sure anything limits people from signing up before')
	waitlist_start_date = models.DateField(help_text='The day waitlist starts, so the day AFTER registration closes')
	freeze_group_date = models.DateField(help_text='The last day people have to form groups on their own')
	league_start_date = models.DateField(help_text='First game of this league night')
	league_end_date = models.DateField(help_text='Last game of this league night')
	paypal_cost = models.IntegerField(help_text='Cost if they pay via paypal')
	check_cost = models.IntegerField(help_text='Cost if they pay via check')
	mail_check_address = models.TextField(help_text='Current treasurer\'s address, or wherever to send the checks')
	max_players = models.IntegerField(help_text='Total number of players that can sign up, if this is reached before waitlist would have normally started, this will force waitlist registration')
	state = models.CharField(max_length=96, choices=LEAGUE_STATE_CHOICES, help_text=''''There are 3 states:<br/>
		Archived: For leagues past, or leagues that were cancelled, this will
		remove the league from the links on the left side of the webpage,<br/>
		Planning: This let\'s us put the info into the system, and people
		signed in with junta priviliges will be able to see it, but not normal
		users,<br/>
		Active: Everyone can see it, and it appears in the side bar links''')
	field = models.ManyToManyField(Field, db_table='field_league', help_text='''Select the fields these games will be played at (Hold
		Ctrl or Apple if you need to select more than one), use
		the green "+" icon if we're playing at a new field''')
	details = models.TextField(help_text='All text to go on details page.  HTML okay')
	league_email = models.CharField(max_length=192, blank=True, help_text='Email address for all players in this league.')
	league_captains_email = models.CharField(max_length=192, blank=True, help_text='Email address for all captains in this league.')
	division_email = models.CharField(max_length=192, blank=True, help_text='Email address for players in just this division (night).')

	class Meta:
		db_table = u'league'

	def get_fields(self):
		return self.fieldleague_set.all()

	def get_league_registrations_for_user(self, user):
		return self.registrations_set.filter(user=user)

	def get_num_game_events(self):
		try:
			return self.schedule_set.all()[0].get_games().count() / (self.team_set.all().count() / 2)
		except:
			return 0

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
	conduct_complete = models.BooleanField()
	waiver_complete = models.BooleanField()
	pay_type = models.TextField(choices=REGISTRATION_PAYMENT_CHOICES, blank=True)
	check_complete = models.BooleanField()
	paypal_invoice_id = models.CharField(max_length=127)
	paypal_complete = models.BooleanField()
	waitlist = models.BooleanField()
	attendance = models.IntegerField(null=True, blank=True)
	captain = models.IntegerField(null=True, blank=True)

	class Meta:
		db_table = u'registrations'

	def get_status(self):
		status = 'Completed'
		if self.conduct_complete:
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
		return bool(self.conduct_complete and self.waiver_complete and self.attendance != None and self.captain != None and self.pay_type and (self.check_complete or self.paypal_complete))

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
		return self.gameteams_set.all()

	def get_user_team(self, user):
		return self.gameteams_set.filter(team__teammember__user=user)[0:1].get().team

	def get_user_opponent(self, user):
		return self.gameteams_set.exclude(team__teammember__user=user)[0:1].get().team

	def get_reports(self):
		return self.gamereport_set.all()

	def report_complete_for_user(self, user):
		for report in self.gamereport_set.filter(team__teammember__user=user, team__teammember__captain=1):
			if (report.is_complete):
				return True
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
