from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.db.models.functions import Lower


from ultimate.utils.email_groups import add_to_group


# Which seasons feed each season's pickup list, as (season_slug, year_offset)
# pairs. year_offset is relative to the target year: 0 = the target year, -1 =
# the previous year. A pickup list is the target season plus the two seasons
# leading into it, so a recent player can be pulled in to fill a roster.
#
# late-fall is the exception: it is one division, so it pulls from summer and
# fall of the same year but is deliberately NOT included in any list itself.
PICKUP_SEASON_WINDOWS = {
    "winter": [("fall", -1), ("late-fall", -1), ("winter", 0)],
    "spring": [("late-fall", -1), ("winter", 0), ("spring", 0)],
    "summer": [("winter", 0), ("spring", 0), ("summer", 0)],
    "fall": [("spring", 0), ("summer", 0), ("fall", 0)],
    "late-fall": [("summer", 0), ("fall", 0)],
}


class Command(BaseCommand):
    help = "Add members to an email group from an email address, file, or team id"

    def add_arguments(self, parser):
        parser.add_argument(
            "-e",
            dest="email",
            default="",
            help="Add single email address",
        )

        parser.add_argument(
            "-f",
            dest="file",
            default="",
            help="Import from a file",
        )

        parser.add_argument(
            "-t",
            type=int,
            dest="team",
            default=0,
            help="Sync a team (team id)",
        )

        parser.add_argument(
            "-l",
            default="",
            dest="league",
            help="Sync a division (league id)",
        )

        parser.add_argument(
            "-s",
            default="",
            dest="season",
            help='Sync a league (season + year), "winter", "spring", "summer", "fall", "late-fall"',
        )

        parser.add_argument(
            "-y",
            default="",
            dest="year",
            help="Sync a league (season + year), e.g. 2019",
        )

        parser.add_argument(
            "-p",
            action="store_true",
            default=False,
            dest="pickup",
            help="Sync a league pickup list",
        )

        parser.add_argument(
            "-g",
            default="",
            dest="group_address",
            help="Group Address (required for email and file)",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            dest="force",
            help="force group create or find (only for team)",
        )

    def _report_sync_result(self, result, group_address):
        """Print the outcome of a diff-based group sync (a GroupSyncResult)."""
        failed = result.failed_add + result.failed_remove

        if not failed:
            self.stdout.write(self.style.SUCCESS("SUCCESS"))
            style = self.style.SUCCESS
        else:
            self.stdout.write(self.style.ERROR("HMMM..."))
            style = self.style.ERROR

        self.stdout.write(
            style(
                "Synced {}: {} added, {} removed, {} total members".format(
                    group_address,
                    len(result.added),
                    len(result.removed),
                    result.target,
                )
            )
        )

        if result.failed_add:
            self.stdout.write(
                self.style.ERROR(
                    "Could not add: {}".format(", ".join(sorted(result.failed_add)))
                )
            )
        if result.failed_remove:
            self.stdout.write(
                self.style.ERROR(
                    "Could not remove: {}".format(
                        ", ".join(sorted(result.failed_remove))
                    )
                )
            )

    def handle(self, *args, **options):
        email_address = options["email"]
        file_path = options["file"]
        team_id = options["team"]
        league_id = options["league"]
        season_slug = options["season"]
        year = options["year"]
        pickup = options["pickup"]
        group_address = options["group_address"]
        force = options["force"]

        if not group_address and (email_address or file_path):
            raise CommandError(
                "group address (-g) is required with email (-e) or file (-f)"
            )

        if (season_slug and not year) or (year and not season_slug):
            raise CommandError("season (-s) and year (-y) must be given together")

        if year and not year.isdigit():
            raise CommandError("year (-y) must be a numeric year, e.g. 2019")

        if email_address:
            self._handle_email(email_address, group_address)
        elif file_path:
            self._handle_file(file_path, group_address)
        elif team_id:
            self._handle_team(team_id, force)
        elif league_id:
            self._handle_league(league_id, force)
        elif season_slug and year:
            self._handle_season(season_slug, year, pickup, force)

    def _handle_email(self, email_address, group_address):
        self.stdout.write(self.style.MIGRATE_HEADING("Adding email address to group:"))
        self.stdout.write("Adding {} to {}...".format(email_address, group_address))

        success_count = add_to_group(
            group_email_address=group_address, email_address=email_address
        )

        if success_count == 1:
            self.stdout.write(self.style.SUCCESS("DONE"))
            self.stdout.write("Added {} to {}...".format(email_address, group_address))
        else:
            self.stdout.write(self.style.ERROR(" HMMM..."))
            self.stdout.write(self.style.ERROR("No email addresses added..."))

    def _handle_file(self, file_path, group_address):
        self.stdout.write(self.style.MIGRATE_HEADING("Adding file to group:"))
        self.stdout.write("Adding file to {}...".format(group_address), ending="")

        success_count = add_to_group(
            group_email_address=group_address, file_path=file_path
        )

        if success_count > 0:
            self.stdout.write(self.style.SUCCESS("DONE"))
        else:
            self.stdout.write(self.style.ERROR(" HMMM..."))
            self.stdout.write(self.style.ERROR("No email addresses added..."))

    def _handle_team(self, team_id, force):
        self.stdout.write(self.style.MIGRATE_HEADING("Syncing team email addresses:"))

        from ultimate.leagues.models import Team

        try:
            team = Team.objects.get(id=team_id)

            result, group_address = team.sync_email_group(force)
            self._report_sync_result(result, group_address)

        except Team.DoesNotExist:
            self.stdout.write(self.style.ERROR("No team found with that id"))

    def _handle_league(self, league_id, force):
        self.stdout.write(
            self.style.MIGRATE_HEADING("Syncing division email addresses:")
        )

        from ultimate.leagues.models import League

        try:
            league = League.objects.get(id=league_id)

            (
                all_result,
                group_address,
                captains_result,
                captains_group_address,
            ) = league.sync_email_groups(force)

            self._report_sync_result(all_result, group_address)
            self._report_sync_result(captains_result, captains_group_address)

        except League.DoesNotExist:
            self.stdout.write(self.style.ERROR("No league division found with that id"))

    def _pickup_emails(self, TeamMember, season_slug, year):
        """Return the set of lowercased member emails for a season's pickup list.

        Builds the query from PICKUP_SEASON_WINDOWS: one (slug, year) clause per
        contributing season, OR'd together.
        """
        year = int(year)
        window = PICKUP_SEASON_WINDOWS.get(season_slug, [])

        season_filter = Q()
        for slug, year_offset in window:
            season_filter |= Q(
                team__league__season__slug=slug,
                team__league__year=str(year + year_offset),
            )

        if not window:
            return set()

        team_members = (
            TeamMember.objects.filter(season_filter)
            .values()
            .annotate(email=Lower("user__email"))
        )

        return {team_member["email"] for team_member in team_members}

    def _handle_season(self, season_slug, year, pickup, force):
        from ultimate.leagues.models import Season, TeamMember

        try:
            season = Season.objects.get(slug=season_slug)

            from ultimate.utils.google_api import GoogleAppsApi

            api = GoogleAppsApi()

            if pickup:
                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "Syncing pickup list for {} {}:".format(season_slug, year[-2:])
                    )
                )

                pickup_email_addresses = self._pickup_emails(
                    TeamMember, season_slug, year
                )

                pickup_group_address = (
                    "{}{}-pickups@lists.annarborultimate.org".format(
                        season.slug, year[-2:]
                    )
                )
                pickup_group_name = "{} {} Pickups".format(season.name, year)
                pickup_group_id = api.prepare_group_for_sync(
                    group_name=pickup_group_name,
                    group_email_address=pickup_group_address,
                    force=force,
                )

                pickup_result = api.sync_group_members(
                    pickup_email_addresses,
                    group_id=pickup_group_id,
                    group_email_address=pickup_group_address,
                )

                self._report_sync_result(pickup_result, pickup_group_address)

            else:
                raise CommandError(
                    "Season list sync (without -p) is not implemented; "
                    "use -p to sync the pickup list."
                )

        except Season.DoesNotExist:
            self.stdout.write(self.style.ERROR("No season found with that slug"))
