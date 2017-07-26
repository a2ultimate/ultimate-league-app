from django.conf import settings
from django.db import models


class GameReport(models.Model):
    team = models.ForeignKey('leagues.Team')
    game = models.ForeignKey('leagues.Game')
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        db_table = u'game_report'

    @property
    def is_complete(self):
        # TODO collapse reports with more than 1 attendance report, more than 2 score sets
        return bool(self.gamereportattendance_set.count() >= 1) and \
            bool(self.gamereportscore_set.count() >= 2)

    def has_comment(self):
        return self.gamereportcomment_set.exclude(comment='').exists()

    def num_players_in_attendance(self):
        return self.gamereportattendance_set.count()

    def num_males_in_attendance(self):
        return self.gamereportattendance_set.filter(user__profile__gender__iexact='M').count()

    def num_females_in_attendance(self):
        return self.gamereportattendance_set.filter(user__profile__gender__iexact='F').count()


class GameReportAttendance(models.Model):
    report = models.ForeignKey('captain.GameReport')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        db_table = u'game_report_attendance'


class GameReportComment(models.Model):
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

    report = models.ForeignKey('captain.GameReport')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    spirit = models.IntegerField(choices=SPIRIT_CHOICES)
    comment = models.TextField()

    class Meta:
        db_table = u'game_report_comment'


class GameReportScore(models.Model):
    report = models.ForeignKey('captain.GameReport')
    team = models.ForeignKey('leagues.Team')
    score = models.IntegerField(blank=False)

    class Meta:
        db_table = u'game_report_scores'
