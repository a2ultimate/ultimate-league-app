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
            self.stdout.write(self.style.MIGRATE_HEADING('Adding team email addresses to group:'))

            from ultimate.leagues.models import Team
            try:
                team = Team.objects.get(id=team_id)

                self.stdout.write(u'Adding Team {}...'.format(team))

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
            self.stdout.write(self.style.MIGRATE_HEADING('Adding division email addresses with group:'))

            from ultimate.leagues.models import League
            try:
                league = League.objects.get(id=league_id)

                self.stdout.write(u'Adding {}...'.format(league))

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
