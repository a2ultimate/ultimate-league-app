import httplib2
import sys

from django.core.management.base import BaseCommand, CommandError

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from ultimate.utils.email_groups import add_to_group


class Command(BaseCommand):
    help = 'Add members to an email group from an email address, file, or team id'

    def add_arguments(self, parser):

        parser.add_argument('-e',
            dest='email',
            default='',
            help='Add single email address')

        parser.add_argument('-f',
            dest='file',
            default='',
            help='Import from a file')

        parser.add_argument('-t',
            type=int,
            dest='team',
            default=0,
            help='Import a team')

        parser.add_argument('-l',
            default='',
            dest='group_address',
            help='Group Address (required for email and file)')

        parser.add_argument('--force',
            action='store_true',
            default=False,
            dest='force',
            help='force group create or find (only for team)')

    def handle(self, *args, **options):
        email_address = options.get('email', None)
        file_path = options.get('file', None)
        team_id = options.get('team', None)
        group_address = options.get('group_address', None)
        force = options.get('force', None)

        success_count = 0

        if not group_address and (email_address or file_path):
            self.stdout.write('group address (-l) is required with email (-e) or file (-f)')
            return

        if email_address:
            success_count = add_to_group(group_email_address=group_address, email_address=email_address)

        elif file_path:
            success_count = add_to_group(group_email_address=group_address, file_path=file_path)

        elif team_id:
            from ultimate.leagues.models import Team
            try:
                team = Team.objects.get(id=team_id)
                success_count, group_address = team.sync_email_group(force)
            except Team.DoesNotExist:
                self.stdout.write('bad team id')

        self.stdout.write('{} email addresses added to {}'.format(success_count, group_address))
