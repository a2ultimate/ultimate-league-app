from django.contrib import admin
from ultimate.captain.models import *


class GameReportAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True

    list_display = ('team', 'game', 'last_updated_by', 'report_scores',)

    def report_scores(self, obj):
        scores = []
        report_scores = obj.gamereportscore_set.all()

        for report_score in report_scores:
            scores.append('{} {}'.format(report_score.team, report_score.score))

        return ', '.join(map(str, scores))


# TODO make this useful, allow score/attendance adjustment, etc.
# admin.site.register(GameReport, GameReportAdmin)
