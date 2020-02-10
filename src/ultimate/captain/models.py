from django.conf import settings
from django.db import models


class GameReport(models.Model):
    team = models.ForeignKey('leagues.Team')
    game = models.ForeignKey('leagues.Game')
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        db_table = 'game_report'

    @property
    def is_complete(self):
        # TODO collapse reports with more than 1 attendance report, more than 2 score sets
        return bool(self.gamereportattendance_set.count() >= 1) and \
            bool(self.gamereportscore_set.count() >= 2)

    @property
    def has_comment(self):
        return self.gamereportcomment_set.exclude(comment='').exists()

    @property
    def has_poor_spirit_comment(self):
        return self.gamereportcomment_set.filter(spirit__lte=5).exists()

    @property
    def num_players_in_attendance(self):
        return self.gamereportattendance_set.count()

    @property
    def num_males_in_attendance(self):
        return self.gamereportattendance_set.filter(user__profile__gender__iexact='M').count()

    @property
    def num_females_in_attendance(self):
        return self.gamereportattendance_set.filter(user__profile__gender__iexact='F').count()


class GameReportAttendance(models.Model):
    report = models.ForeignKey('captain.GameReport')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        db_table = 'game_report_attendance'


class GameReportComment(models.Model):
    SPIRIT_CHOICES = (
        ('', ''),
        (10, '10'),
        (9, '9'),
        (8, '8'),
        (7, '7 - Average'),
        (6, '6'),
        (5, '5'),
        (4, '4'),
        (3, '3'),
        (2, '2'),
        (1, '1'),
        (0, '0'),
    )

    report = models.ForeignKey('captain.GameReport')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    spirit = models.IntegerField(choices=SPIRIT_CHOICES)
    comment = models.TextField()

    class Meta:
        db_table = 'game_report_comment'


class GameReportScore(models.Model):
    report = models.ForeignKey('captain.GameReport')
    team = models.ForeignKey('leagues.Team')
    score = models.IntegerField(blank=False)

    class Meta:
        db_table = 'game_report_scores'
