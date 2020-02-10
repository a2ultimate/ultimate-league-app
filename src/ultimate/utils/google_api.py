from datetime import datetime
import dateutil.parser
import httplib2
import logging

from django.conf import settings
from django.utils.timezone import make_aware

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger('a2u.email_groups')


class GoogleAppsApi:
    http = None
    service = None

    def __init__(self):
        credentials_file = getattr(settings, 'GOOGLE_APPS_API_CREDENTIALS_FILE', False)
        scopes = getattr(settings, 'GOOGLE_APPS_API_SCOPES', False)
        account = getattr(settings, 'GOOGLE_APPS_API_ACCOUNT', False)

        if credentials_file and scopes and account:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                credentials_file, scopes=scopes)

            credentials._kwargs['sub'] = account

            self.http = httplib2.Http()
            self.http = credentials.authorize(self.http)

    def prepare_group_for_sync(self, group_name, group_id=None, group_email_address=None, force=False):
        logger.debug('Preparing group "{}" for sync...'.format(group_name))

        if force:
            self.delete_group(group_id=group_id, group_email_address=group_email_address)
        else:
            self.remove_all_group_members(
                group_id=group_id,
                group_email_address=group_email_address,
                group_name=group_name)

        return self.get_or_create_group(
            group_email_address=group_email_address, group_name=group_name)

    # TODO need paging for when you have over 200 groups
    def get_or_create_group(self, group_email_address, group_name=''):
        logger.debug('  Getting or creating group {}...'.format(group_email_address))

        service = build('admin', 'directory_v1', http=self.http, cache_discovery=False)

        groups_response = None
        target_group = None

        try:
            logger.debug('    Looking for existing group...')
            groups_response = service.groups().list(customer='my_customer', domain='lists.annarborultimate.org', query='email={}'.format(group_email_address)).execute(http=self.http)
        except Exception as e:
            return None

        if groups_response and groups_response.get('groups'):
            for group in groups_response.get('groups'):
                if group.get('email') == group_email_address:
                    logger.debug('    Group found!')
                    target_group = group

        # couldn't find group, create it
        if not target_group:
            logger.debug('    Group not found...creating {}...'.format(group_email_address))

            body = { 'email': group_email_address, }
            if group_name:
                body.update({ 'name': group_name, })

            try:
                target_group = service.groups().insert(body=body).execute(http=self.http)
                logger.debug('    Success!')
            except Exception as e:
                logger.debug('    Failure!')
                return None

        group_id = target_group.get('id', None)

        return group_id

    def delete_group(self, group_id=None, group_email_address=None):
        logger.debug('  Deleting existing group...')

        service = build('admin', 'directory_v1', http=self.http, cache_discovery=False)

        if group_email_address and not group_id:
            try:
                groups_response = service.groups().list(customer='my_customer', domain='lists.annarborultimate.org', query='email={}'.format(group_email_address)).execute(http=self.http)

                if groups_response and groups_response.get('groups'):
                    for group in groups_response.get('groups'):
                        if group.get('email') == group_email_address:
                            group_id = group.get('id', None)
            except Exception as e:
                return False

        if group_id:
            try:
                service.groups().delete(groupKey=group_id).execute(http=self.http)
                logger.debug('    Success!')
            except Exception as e:
                logger.debug('    Failure!')
                return False

        return True

    def remove_all_group_members(self, group_id=None, group_email_address=None, group_name=None):
        logger.debug('  Removing all members from {}...'.format(group_email_address))

        service = build('admin', 'directory_v1', http=self.http, cache_discovery=False)

        if group_email_address and not group_id:
            try:
                groups_response = service.groups().list(customer='my_customer', domain='lists.annarborultimate.org', query='email={}'.format(group_email_address)).execute(http=self.http)

                if groups_response and groups_response.get('groups'):
                    for group in groups_response.get('groups'):
                        if group.get('email') == group_email_address:
                            group_id = group.get('id', None)
            except Exception as e:
                logger.debug('    Group could not be found')
                return False

        if group_id:
            try:
                members_response = service.members().list(groupKey=group_id).execute(http=self.http)
                if members_response and members_response.get('members'):
                    for member in members_response.get('members'):
                        member_id = member.get('id', None)
                        service.members().delete(groupKey=group_id, memberKey=member_id).execute(http=self.http)
            except Exception as e:
                logger.debug('    Group could not be found')
                return False

        logger.debug('    Done')

    def add_group_member(self, email_address, group_id=None, group_email_address=None, group_name=None):
        logger.debug('Adding {} to {}...'.format(email_address, group_email_address or 'group'))

        service = build('admin', 'directory_v1', http=self.http, cache_discovery=False)

        body = {
            'email': email_address,
            'role': 'MEMBER'
        }
        response = False

        # look for group
        if not group_id and group_email_address:
            group_id = self.get_or_create_group(
                group_email_address=group_email_address, group_name=group_name)

        if group_id:
            try:
                response = service.members().insert(groupKey=group_id, body=body).execute(http=self.http)
                logger.debug('  Success!')
            except:
                logger.debug('  Failure!')
                return False

        return response

    def get_calendar_events(self, calendar_id, since, until):
        service = build(serviceName='calendar', version='v3', http=self.http, cache_discovery=False)

        since = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - since).isoformat('T') + 'Z'
        until = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + until).isoformat('T') + 'Z'

        try:
            events_response = service.events().list(
                calendarId=calendar_id,
                orderBy='startTime',
                singleEvents=True,
                timeMin=since,
                timeMax=until,
            ).execute(http=self.http)
        except Exception as e:
            return None

        events = []
        for event in events_response['items']:
            events.append({
                'summary': event.get('summary'),
                'start': dateutil.parser.parse(event['start']['dateTime']),
                'end': event['end']['dateTime'],
                'location': event.get('location'),
                'description': event.get('description'),
            })

        return events
