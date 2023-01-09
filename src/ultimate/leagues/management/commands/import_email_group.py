import httplib2
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.db.models.functions import Lower

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
            help='Sync a division (league id)',
        )

        parser.add_argument(
            '-s',
            default='',
            dest='season',
            help='Sync a league (season + year), "winter", "spring", "summer", "fall", "late-fall"',
        )

        parser.add_argument(
            '-y',
            default='',
            dest='year',
            help='Sync a league (season + year), e.g. 2019',
        )

        parser.add_argument(
            '-p',
            action='store_true',
            default=False,
            dest='pickup',
            help='Sync a league pickup list',
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
        pickup = options.get('pickup', None)
        group_address = options.get('group_address', None)
        force = options.get('force', None)

        success_count = 0

        if not group_address and (email_address or file_path):
            raise CommandError('group address (-g) is required with email (-e) or file (-f)')

        if email_address:
            self.stdout.write(self.style.MIGRATE_HEADING('Adding email address to group:'))
            self.stdout.write('Adding {} to {}...'.format(email_address, group_address))

            success_count = add_to_group(group_email_address=group_address, email_address=email_address)

            if success_count == 1:
                self.stdout.write(self.style.SUCCESS('DONE'))
                self.stdout.write('Added {} to {}...'.format(email_address, group_address))
            else:
                self.stdout.write(self.style.ERROR(' HMMM...'))
                self.stdout.write(self.style.ERROR('No email addresses added...'))

        elif file_path:
            self.stdout.write(self.style.MIGRATE_HEADING('Adding file to group:'))
            self.stdout.write('Adding file to {}...'.format(group_address), ending='')

            success_count = add_to_group(group_email_address=group_address, file_path=file_path)

            if success_count > 0:
                self.stdout.write(self.style.SUCCESS('DONE'))
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
                    self.stdout.write(self.style.SUCCESS('SUCCESS'))
                    self.stdout.write(self.style.SUCCESS('Added {} of {} email addresses to {}'.format(success_count, target_count, group_address)))
                elif success_count > 0:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR('Added {} of {} email addresses to {}'.format(success_count, target_count, group_address)))
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
                    self.stdout.write(self.style.SUCCESS('SUCCESS'))
                    self.stdout.write(self.style.SUCCESS('Added {} of {} email addresses to {}'.format(all_success_count, all_target_count, group_address)))
                    self.stdout.write(self.style.SUCCESS('Added {} of {} email addresses to {}'.format(captains_success_count, captains_target_count, captains_group_address)))
                elif all_success_count > 0 or captains_success_count > 0:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR('Added {} of {} email addresses to {}'.format(all_success_count, all_target_count, group_address)))
                    self.stdout.write(self.style.ERROR('Added {} of {} email addresses to {}'.format(captains_success_count, captains_target_count, captains_group_address)))
                else:
                    self.stdout.write(self.style.ERROR('HMMM...'))
                    self.stdout.write(self.style.ERROR('No email addresses added...'))

            except League.DoesNotExist:
                self.stdout.write(self.style.ERROR('No league division found with that id'))

        elif season_slug and year:

            from ultimate.leagues.models import Season, TeamMember
            try:
                season = Season.objects.get(slug=season_slug)

                from ultimate.utils.google_api import GoogleAppsApi
                api = GoogleAppsApi()

                if pickup:
                    self.stdout.write(self.style.MIGRATE_HEADING('Syncing pickup list for {} {}:'.format(season_slug, year[-2:])))

                    pickup_team_members = []
                    previous_year = str(int(year) - 1)

                    if season_slug == 'winter':
                        pickup_team_members = TeamMember.objects.filter(Q(Q(Q(team__league__season__slug='fall') & Q(team__league__year=previous_year)) |
                            Q(Q(team__league__season__slug='late-fall') & Q(team__league__year=previous_year)) |
                            Q(Q(team__league__season__slug='winter') & Q(team__league__year=year)))).values().annotate(email=Lower('user__email')).order_by('user__email')
                    elif season_slug == 'spring':
                        pickup_team_members = TeamMember.objects.filter(Q(Q(Q(team__league__season__slug='late-fall') & Q(team__league__year=previous_year)) |
                            Q(Q(team__league__season__slug='winter') & Q(team__league__year=year)) |
                            Q(Q(team__league__season__slug='spring') & Q(team__league__year=year)))).values().annotate(email=Lower('user__email')).order_by('user__email')
                    elif season_slug == 'summer':
                        pickup_team_members = TeamMember.objects.filter(Q(Q(Q(team__league__season__slug='winter') & Q(team__league__year=year)) |
                            Q(Q(team__league__season__slug='spring') & Q(team__league__year=year)) |
                            Q(Q(team__league__season__slug='summer') & Q(team__league__year=year)))).values().annotate(email=Lower('user__email')).order_by('user__email')
                    elif season_slug == 'fall':
                        pickup_team_members = TeamMember.objects.filter(Q(Q(Q(team__league__season__slug='spring') & Q(team__league__year=year)) |
                            Q(Q(team__league__season__slug='summer') & Q(team__league__year=year)) |
                            Q(Q(team__league__season__slug='fall') & Q(team__league__year=year)))).values().annotate(email=Lower('user__email')).order_by('user__email')
                    elif season_slug == 'late-fall':
                        # do not include late fall since there is only one division
                        pickup_team_members = TeamMember.objects.filter(Q(Q(Q(team__league__season__slug='summer') & Q(team__league__year=year)) |
                            Q(Q(team__league__season__slug='fall') & Q(team__league__year=year)))).values().annotate(email=Lower('user__email')).order_by('user__email')

                    pickup_email_addresses = list(set([ptm['email'] for ptm in pickup_team_members]))

                    pickup_group_address = '{}{}-pickups@lists.annarborultimate.org'.format(season.slug, year[-2:])
                    pickup_group_name = '{} {} Pickups'.format(season.name, year)
                    pickup_group_id = api.prepare_group_for_sync(
                        group_name=pickup_group_name,
                        group_email_address=pickup_group_address,
                        force=force)

                    pickup_target_count = len(pickup_email_addresses)
                    pickup_success_count = 0
                    for pickup_email_address in pickup_email_addresses:
                        pickup_success_count += add_to_group(
                            group_email_address=pickup_group_address,
                            group_id=pickup_group_id,
                            email_address=pickup_email_address)

                    if pickup_success_count == pickup_target_count:
                        self.stdout.write(self.style.SUCCESS('SUCCESS'))
                        self.stdout.write(self.style.SUCCESS('Added {} of {} email addresses to {}'.format(pickup_success_count, pickup_target_count, pickup_group_address)))
                    else:
                        self.stdout.write(self.style.ERROR('HMMM...'))
                        self.stdout.write(self.style.ERROR('Added {} of {} email addresses to {}'.format(pickup_success_count, pickup_target_count, pickup_group_address)))

                else:
                    self.stdout.write(self.style.MIGRATE_HEADING('Syncing season list for {} {}:'.format(season_slug, year[-2:])))

                    return
                    # ALL

                    all_group_address = '{}{}@lists.annarborultimate.org'.format(season.slug, year[-2:])
                    all_group_name = '{} {}'.format(season.name, year)
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

                    men_group_address = '{}{}-men@lists.annarborultimate.org'.format(season.slug, year[-2:])
                    men_group_name = '{} {} Men'.format(season.name, year)
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

                    women_group_address = '{}{}-women@lists.annarborultimate.org'.format(season.slug, year[-2:])
                    women_group_name = '{} {} Women'.format(season.name, year)
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
                        self.stdout.write(self.style.SUCCESS('SUCCESS'))
                        self.stdout.write(self.style.SUCCESS('Added {} of {} email addresses to {}'.format(all_success_count, all_target_count, all_group_address)))
                    else:
                        self.stdout.write(self.style.ERROR('HMMM...'))
                        self.stdout.write(self.style.ERROR('Added {} of {} email addresses to {}'.format(all_success_count, all_target_count, all_group_address)))

                    if men_success_count == men_team_members.count():
                        self.stdout.write(self.style.SUCCESS('SUCCESS'))
                        self.stdout.write(self.style.SUCCESS('Added {} of {} email addresses to {}'.format(men_success_count, men_target_count, men_group_address)))
                    else:
                        self.stdout.write(self.style.ERROR('HMMM...'))
                        self.stdout.write(self.style.ERROR('Added {} of {} email addresses to {}'.format(men_success_count, men_target_count, men_group_address)))

                    if women_success_count == women_team_members.count():
                        self.stdout.write(self.style.SUCCESS('SUCCESS'))
                        self.stdout.write(self.style.SUCCESS('Added {} of {} email addresses to {}'.format(women_success_count, women_target_count, women_group_address)))
                    else:
                        self.stdout.write(self.style.ERROR('HMMM...'))
                        self.stdout.write(self.style.ERROR('Added {} of {} email addresses to {}'.format(women_success_count, women_target_count, women_group_address)))

            except Season.DoesNotExist:
                self.stdout.write(self.style.ERROR('No season found with that slug'))

