from django.db import models
from django.contrib.auth.models import User

SPIRIT_CHOICES = (
	('', u''),
	(10, u'10 - Awesome'),
	(9, u'9'),
	(8, u'8 - Great'),
	(7, u'7'),
	(6, u'6 - Good'),
	(5, u'5'),
	(4, u'4 - Okay'),
	(3, u'3'),
	(2, u'2 - Bad'),
	(1, u'1'),
	(0, u'0 - Awful'),
)

class GameReport(models.Model):
	id = models.AutoField(primary_key=True)
	team = models.ForeignKey('leagues.Team')
	game = models.ForeignKey('leagues.Game')
	last_updated_by = models.ForeignKey(User)

	class Meta:
		db_table = u'game_report'

	@property
	def is_complete(self):
		# TODO collapse reports with more than 1 attendance report, more than 2 score sets
		return bool(self.gamereportattendance_set.count() >= 1) and \
			bool(self.gamereportscore_set.count() >= 2)

class GameReportAttendance(models.Model):
	id = models.AutoField(primary_key=True)
	report = models.ForeignKey('captain.GameReport')
	user = models.ForeignKey(User)

	class Meta:
		db_table = u'game_report_attendance'

class GameReportComment(models.Model):
	id = models.AutoField(primary_key=True)
	report = models.ForeignKey('captain.GameReport')
	submitted_by = models.ForeignKey(User)
	spirit = models.IntegerField(choices=SPIRIT_CHOICES)
	comment = models.TextField()

	class Meta:
		db_table = u'game_report_comment'

class GameReportScore(models.Model):
	id = models.AutoField(primary_key=True)
	report = models.ForeignKey('captain.GameReport')
	team = models.ForeignKey('leagues.Team')
	score = models.IntegerField(blank=False)

	class Meta:
		db_table = u'game_report_scores'
