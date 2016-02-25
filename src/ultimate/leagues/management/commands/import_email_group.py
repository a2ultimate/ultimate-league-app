import httplib2
import sys

from django.core.management.base import BaseCommand, CommandError

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from ultimate.utils.email_groups import add_to_group

# https://developers.google.com/resources/api-libraries/documentation/admin/directory_v1/python/latest/index.html

class Command(BaseCommand):
    help = 'Add members to an email group from an email address, file, or team id'

    def add_arguments(self, parser):

        parser.add_argument('-e',
            dest='email',
            default='',
            help='Import from a file')

        parser.add_argument('-f',
            dest='file',
            default='',
            help='Import from a file')

        parser.add_argument('-t',
            type=int,
            dest='team',
            default=0,
            help='Import a team')

        parser.add_argument('list_address')

    def handle(self, *args, **options):
        email_address = options.get('email', None)
        file_path = options.get('file', None)
        team_id = options.get('team', None)
        group_address = options.get('list_address', None)

        if email_address:
            success_count = add_to_group(group_email_address=group_address, email_address=email_address)

        elif file_path:
            success_count = add_to_group(group_email_address=group_address, file_path=file_path)

        elif team_id:
            self.stdout.write(team_id)

        self.stdout.write('{} email addresses added to {}'.format(success_count, group_address))
