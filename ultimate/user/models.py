from django.db import models
from django.contrib.auth.models import User

from ultimate.leagues.models import *


class PlayerRatings(models.Model):

	RATING_EXPERIENCE_CHOICES = (
		(1,	'I am new to ultimate or have played less than 2 years of pickup.'),
		(2,	'I have played in an organized league or on a high school team for 1-2 seasons, or pickup for 3+ years.'),
		(3,	'I have played in an organized league or on a high school team for 3+ seasons.'),
		(4, 'I have played on a college or club team in the last 6 years.'),
		(5,	'I have played multiple seasons on a college or club team in the last 4 years.'),
		(6,	'I have played multiple seasons on a regionals or nationals-level college or club team in the last 4 years.'),
	)

	RATING_STRATEGY_CHOICES = (
		(1,	'I am new to organized ultimate.'),
		(2,	'I have basic knowledge of the game (e.g. stall counts, pivoting).'),
		(3,	'I have moderate knowledge (e.g. vertical stack, force, basic man defense).'),
		(4,	'I have advanced knowledge (e.g. zone defense, horizontal stack, switching).'),
		(5,	'I am familiar enough with the above concepts that I could explain them to a new player.'),
		(6,	'I would consider myself an expert in ultimate strategy.'),
	)

	RATING_THROWING_CHOICES = (
		(1,	'I am a novice or am learning to throw.'),
		(2,	'I can throw a backhand 10 yards with 90% confidence.'),
		(3,	'I can throw a forehand 10+ yards with 90% confidence and can handle if needed.'),
		(4,	'I am confident throwing forehand and backhand various distances and can handle at a league level.'),
		(5,	'I am confident throwing break throws and can be a very good league-level handler.'),
		(6,	'I am confident in many styles of throws and could be a college or club-level handler.'),
	)

	RATING_ATHLETICISM_CHOICES = (
		(1,	'I am slow, it is hard to change direction, and am easily winded.'),
		(2,	'I can change direction decently, but need to rest often.'),
		(3,	'I am somewhat fast, can make hard cuts, and can play for a few minutes at a time before resting.'),
		(4,	'I am fairly fast, can change direction and react well, and can play a few hard points in a row.'),
		(5,	'I am very fast, can turn well, jump high, and need little rest.'),
		(6,	'I am faster than anyone on the field at any level and enjoy playing almost every point.'),
	)

	RATING_COMPETITIVENESS_CHOICES = (
		(1,	'I do not care whether I win or lose, I play purely to socialize and have fun.'),
		(2,	'I play ultimate to have fun, but would prefer to win.'),
		(3,	'I am competitive, fight to win close games, and am somewhat disappointed by a loss.'),
		(4,	'I am extremely competitive and am very disappointed by a loss.'),
	)

	RATING_TYPE_CAPTAIN = 1
	RATING_TYPE_JUNTA = 2
	RATING_TYPE_USER = 3
	RATING_TYPE = (
		(RATING_TYPE_CAPTAIN,	'Captain'),
		(RATING_TYPE_JUNTA,		'Junta'),
		(RATING_TYPE_USER,		'User'),
	)

	id = models.AutoField(primary_key=True)

	experience = models.PositiveIntegerField(default=None, choices=RATING_EXPERIENCE_CHOICES, blank=True, null=True)
	strategy = models.PositiveIntegerField(default=None, choices=RATING_STRATEGY_CHOICES, blank=True, null=True)
	throwing = models.PositiveIntegerField(default=None, choices=RATING_THROWING_CHOICES, blank=True, null=True)
	athleticism = models.PositiveIntegerField(default=None, choices=RATING_ATHLETICISM_CHOICES, blank=True, null=True)
	competitiveness = models.PositiveIntegerField(default=None, choices=RATING_COMPETITIVENESS_CHOICES, blank=True, null=True)
	spirit = models.PositiveIntegerField(default=None, blank=True, null=True)
	user = models.ForeignKey(User)
	submitted_by = models.ForeignKey(User, related_name='ratings_submitted_by_set')
	ratings_type = models.PositiveIntegerField(choices=RATING_TYPE)
	ratings_report = models.ForeignKey('user.PlayerRatingsReport', blank=True, null=True)
	not_sure = models.BooleanField(default=False)
	updated = models.DateTimeField(auto_now=True, auto_now_add=True)

	class Meta:
		db_table = u'player_ratings'
		verbose_name_plural = 'player ratings'

	def save(self, *args, **kwargs):
		if not self.experience:
			self.experience = None
		if not self.strategy:
			self.strategy = None
		if not self.throwing:
			self.throwing = None
		if not self.athleticism:
			self.athleticism = None
		if not self.competitiveness:
			self.competitiveness = None
		if not self.spirit:
			self.spirit = None
		super(PlayerRatings, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s %s <- %s' % (str(self.updated), self.user, self.submitted_by)


class PlayerRatingsReport(models.Model):
	id = models.AutoField(primary_key=True)
	submitted_by = models.ForeignKey(User, related_name='ratings_report_submitted_by_set')
	team = models.ForeignKey('leagues.Team')
	updated = models.DateTimeField()

	class Meta:
		db_table = u'player_ratings_report'

	def __unicode__(self):
		return '%s, %s, %s' % (self.team, self.team.league, self.submitted_by)
