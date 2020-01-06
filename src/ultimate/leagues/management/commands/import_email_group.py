import httplib2
import sys

from django.core.management.base import BaseCommand, CommandError

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from ultimate.utils.email_groups import add_to_group


class Command(BaseCommand):
    help = 'Add members to an email group from an email address, file, or team id'

    def add_arguments(self, parser):
        parser.add_argument(
            '-e',
            dest='email',
            default='',
            help='Add single email address',
        )

        parser.add_argument(
            '-f',
            dest='file',
            default='',
            help='Import from a file',
        )

        parser.add_argument(
            '-t',
            type=int,
            dest='team',
            default=0,
            help='Sync a team (team id)',
        )

        parser.add_argument(
            '-l',
            default='',
            dest='league',
            help='Sync a league (league id)',
        )

        parser.add_argument(
            '-s',
            default='',
            dest='season',
            help='Sync a season + year ("winter", "spring", "summer", "fall", "late-fall")',
        )

        parser.add_argument(
            '-y',
            default='',
            dest='year',
            help='Sync a season + year (e.g. 2019)',
        )

        parser.add_argument(
            '-g',
            default='',
            dest='group_address',
            help='Group Address (required for email and file)',
        )

        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            dest='force',
            help='force group create or find (only for team)',
        )

    def handle(self, *args, **options):
        email_address = options.get('email', None)
        file_path = options.get('file', None)
        team_id = options.get('team', None)
        league_id = options.get('league', None)
        season_slug = options.get('season', None)
        year = options.get('year', None)
        group_address = options.get('group_address', None)
        force = options.get('force', None)

        success_count = 0

        if not group_address and (email_address or file_path):
            raise CommandError('group address (-g) is required with email (-e) or file (-f)')

        if email_address:
            self.stdout.write(self.style.MIGRATE_HEADING('Adding email address to group:'))
            self.stdout.write(u'Adding {} to {}...'.format(email_address, group_address))

            success_count = add_to_group(group_email_address=group_address, email_address=email_address)

            if success_count == 1:
                self.stdout.write(self.style.MIGRATE_SUCCESS('DONE'))
                self.stdout.write(u'Added {} to {}...'.format(email_address, group_address))
            else:
                self.stdout.write(self.style.ERROR(' HMMM...'))
                self.stdout.write(self.style.ERROR('No email addresses added...'))

        elif file_path:
            self.stdout.write(self.style.MIGRATE_HEADING('Adding file to group:'))
            self.stdout.write(u'Adding file to {}...'.format(group_address), ending='')

            success_count = add_to_group(group_email_address=group_address, file_path=file_path)

            if success_count > 0:
                self.stdout.write(self.style.MIGRATE_SUCCESS('DONE'))
            else:
                self.stdout.write(self.style.ERROR(' HMMM...'))
                self.stdout.write(self.style.ERROR('No email addresses added...'))

        elif team_id:
            self.stdout.write(self.style.MIGRATE_HEADING('Syncing team email addresses:'))

            from ultimate.leagues.models import Team
            try:
                team = Team.objects.get(id=team_id)

                success_count, group_address = team.sync_email_group(force)
                target_count = team.size

                if success_count == target_count:
                    self.stdout.write(self.style.MIGRATE_SUCCESS('SUCCESS'))
                    self.stdout.write(self.style.MIGRATE_SUCCESS(u'Added {} of {} email addresses to {}'.format(success_count, target_count, group_address)))
                elif success_count > 0:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR(u'Added {} of {} email addresses to {}'.format(success_count, target_count, group_address)))
                else:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR('No email addresses added...'))

            except Team.DoesNotExist:
                self.stdout.write(self.style.ERROR('No team found with that id'))

        elif league_id:
            self.stdout.write(self.style.MIGRATE_HEADING('Syncing division email addresses:'))

            from ultimate.leagues.models import League
            try:
                league = League.objects.get(id=league_id)

                all_success_count, group_address, captains_success_count, captains_group_address = \
                    league.sync_email_groups(force)

                all_target_count = league.get_player_count()
                captains_target_count = league.get_captain_count()

                if all_success_count == all_target_count and captains_success_count == captains_target_count:
                    self.stdout.write(self.style.MIGRATE_SUCCESS('SUCCESS'))
                    self.stdout.write(self.style.MIGRATE_SUCCESS(u'Added {} of {} email addresses to {}'.format(all_success_count, all_target_count, group_address)))
                    self.stdout.write(self.style.MIGRATE_SUCCESS(u'Added {} of {} email addresses to {}'.format(captains_success_count, captains_target_count, captains_group_address)))
                elif all_success_count > 0 or captains_success_count > 0:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR(u'Added {} of {} email addresses to {}'.format(all_success_count, all_target_count, group_address)))
                    self.stdout.write(self.style.ERROR(u'Added {} of {} email addresses to {}'.format(captains_success_count, captains_target_count, captains_group_address)))
                else:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR('No email addresses added...'))

            except League.DoesNotExist:
                self.stdout.write(self.style.ERROR('No league division found with that id'))

        elif season_slug and year:
            self.stdout.write(self.style.MIGRATE_HEADING(u'Syncing season email addresses for {} {}:'.format(season_slug, year[-2:])))

            from ultimate.leagues.models import Season, TeamMember
            try:
                season = Season.objects.get(slug=season_slug)

                from ultimate.utils.google_api import GoogleAppsApi
                api = GoogleAppsApi()

                # ALL

                all_group_address = u'{}{}@lists.annarborultimate.org'.format(season.slug, year[-2:])
                all_group_name = u'{} {}'.format(season.name, year)
                all_group_id = api.prepare_group_for_sync(
                    group_name=all_group_name,
                    group_email_address=all_group_address,
                    force=force)

                all_team_members = TeamMember.objects.filter(team__league__season__slug=season.slug, team__league__year=year)
                all_target_count = all_team_members.count()
                all_success_count = 0
                for team_member in all_team_members:
                    all_success_count += add_to_group(
                        group_email_address=all_group_address,
                        group_id=all_group_id,
                        email_address=team_member.user.email)

                # MEN

                men_group_address = u'{}{}-men@lists.annarborultimate.org'.format(season.slug, year[-2:])
                men_group_name = u'{} {} Men'.format(season.name, year)
                men_group_id = api.prepare_group_for_sync(
                    group_name=men_group_name,
                    group_email_address=men_group_address,
                    force=force)

                men_team_members = TeamMember.objects.filter(team__league__season__slug=season.slug, team__league__year=year, user__profile__gender__iexact='M')
                men_target_count = men_team_members.count()
                men_success_count = 0
                for team_member in men_team_members:
                    men_success_count += add_to_group(
                        group_email_address=men_group_address,
                        group_id=men_group_id,
                        email_address=team_member.user.email)

                # WOMEN

                women_group_address = u'{}{}-women@lists.annarborultimate.org'.format(season.slug, year[-2:])
                women_group_name = u'{} {} Women'.format(season.name, year)
                women_group_id = api.prepare_group_for_sync(
                    group_name=women_group_name,
                    group_email_address=women_group_address,
                    force=force)

                women_team_members = TeamMember.objects.filter(team__league__season__slug=season.slug, team__league__year=year, user__profile__gender__iexact='F')
                women_target_count = women_team_members.count()
                women_success_count = 0
                for team_member in women_team_members:
                    women_success_count += add_to_group(
                        group_email_address=women_group_address,
                        group_id=women_group_id,
                        email_address=team_member.user.email)


                if all_success_count == all_team_members.count():
                    self.stdout.write(self.style.MIGRATE_SUCCESS('SUCCESS'))
                    self.stdout.write(self.style.MIGRATE_SUCCESS(u'Added {} of {} email addresses to {}'.format(all_success_count, all_target_count, all_group_address)))
                else:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR(u'Added {} of {} email addresses to {}'.format(all_success_count, all_target_count, all_group_address)))

                if men_success_count == men_team_members.count():
                    self.stdout.write(self.style.MIGRATE_SUCCESS('SUCCESS'))
                    self.stdout.write(self.style.MIGRATE_SUCCESS(u'Added {} of {} email addresses to {}'.format(men_success_count, men_target_count, men_group_address)))
                else:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR(u'Added {} of {} email addresses to {}'.format(men_success_count, men_target_count, men_group_address)))

                if women_success_count == women_team_members.count():
                    self.stdout.write(self.style.MIGRATE_SUCCESS('SUCCESS'))
                    self.stdout.write(self.style.MIGRATE_SUCCESS(u'Added {} of {} email addresses to {}'.format(women_success_count, women_target_count, women_group_address)))
                else:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR(u'Added {} of {} email addresses to {}'.format(women_success_count, women_target_count, women_group_address)))


            except Season.DoesNotExist:
                self.stdout.write(self.style.ERROR('No season found with that slug'))
