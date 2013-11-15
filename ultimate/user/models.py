from django.db import models
from django.contrib.auth.models import User

from ultimate.leagues.models import *


class PlayerRatings(models.Model):

	RATING_EXPERIENCE_CHOICES = (
		(1,	'I am new to ultimate.'),
		(2,	'I have played pickup, but for less than 3 years.'),
		(3,	'I have played in an organized league for 1-2 seasons, or pickup for 3+ years.'),
		(4,	'I have played in an organized league for 3+ seasons.'),
		(5,	'I have played on a college or club team in the last 3 years.'),
		(6,	'I have played on a regionals or nationals-level college or club team for 2 of the last 3 years.'),
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

	experience = models.PositiveIntegerField(default=0, choices=RATING_EXPERIENCE_CHOICES)
	strategy = models.PositiveIntegerField(default=0, choices=RATING_STRATEGY_CHOICES)
	throwing = models.PositiveIntegerField(default=0, choices=RATING_THROWING_CHOICES)
	athleticism = models.PositiveIntegerField(default=0, choices=RATING_ATHLETICISM_CHOICES)
	competitiveness = models.PositiveIntegerField(default=0, choices=RATING_COMPETITIVENESS_CHOICES)
	spirit = models.PositiveIntegerField(default=0)
	user = models.ForeignKey(User)
	submitted_by = models.ForeignKey(User, related_name='skills_submitted_by_set')
	ratings_type = models.CharField(default=None, choices=RATING_TYPE, blank=True, null=True)
	ratings_report = models.ForeignKey('leagues.SkillsReport')
	updated = models.DateTimeField(auto_now=True, auto_now_add=True)

	class Meta:
		db_table = u'player_ratings'

	def __unicode__(self):
		return '%s %s <- %s' % (str(self.updated), self.user, self.submitted_by)