from datetime import datetime, time
import random
from math import floor

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, F
from django.db.transaction import atomic
from django.template.defaultfilters import slugify
from django.utils import timezone

from ultimate.utils.email_groups import (
    add_to_group,
    generate_email_list_address,
    generate_email_list_name,
)


def generateLeagueCoverImagePath(instance, filename):
    return "images/{}/{}/{}/{}".format(
        instance.year, instance.season.slug, instance.night_slug, filename
    )


class Field(models.Model):
    FIELD_TYPE_INDOOR = "indoor"
    FIELD_TYPE_OUTDOOR = "outdoor"
    FIELD_TYPE_CHOICES = (
        (FIELD_TYPE_INDOOR, "Indoor"),
        (FIELD_TYPE_OUTDOOR, "Outdoor"),
    )

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    layout_link = models.TextField(blank=True)
    address = models.TextField(blank=True)
    driving_link = models.TextField(blank=True)
    note = models.TextField(blank=True)
    type = models.CharField(max_length=32, choices=FIELD_TYPE_CHOICES)

    class Meta:
        db_table = "field"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def display_type(self):
        return dict(self.FIELD_TYPE_CHOICES)[self.type]


class FieldNames(models.Model):
    FIELD_TYPE_GRASS = "grass"
    FIELD_TYPE_TURF = "turf"
    FIELD_TYPE_CHOICES = (
        (FIELD_TYPE_GRASS, "Grass"),
        (FIELD_TYPE_TURF, "Turf"),
    )

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    field = models.ForeignKey("leagues.Field")
    hidden = models.BooleanField(default=False)
    type = models.CharField(max_length=32, choices=FIELD_TYPE_CHOICES)

    class Meta:
        db_table = "field_names"
        verbose_name_plural = "field names"
        ordering = ["field__name", "name"]

    def __str__(self):
        return "{} {}".format(self.field.name, self.name)


class Season(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField()

    order = models.IntegerField(null=True, default=None)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)

        super(Season, self).save()


class League(models.Model):
    LEAGUE_STATE_CANCELLED = "cancelled"
    LEAGUE_STATE_CLOSED = "closed"
    LEAGUE_STATE_HIDDEN = "hidden"
    LEAGUE_STATE_OPEN = "open"
    LEAGUE_STATE_PREVIEW = "preview"
    LEAGUE_STATE_CHOICES = (
        (
            LEAGUE_STATE_CANCELLED,
            "Cancelled - visible to all, registration closed to all",
        ),
        (LEAGUE_STATE_CLOSED, "Closed - visible to all, registration closed to all"),
        (LEAGUE_STATE_HIDDEN, "Hidden - hidden to all, registration closed to all"),
        (
            LEAGUE_STATE_OPEN,
            "Open - visible to all, registration conditionally open to all",
        ),
        (
            LEAGUE_STATE_PREVIEW,
            "Preview - visible only to admins, registration conditionally open only to admins",
        ),
    )

    LEAGUE_GENDER_CAPANDFILL = "capandfill"
    LEAGUE_GENDER_COREC = "corec"
    LEAGUE_GENDER_MENS = "mens"
    LEAGUE_GENDER_MIXED = "mixed"
    LEAGUE_GENDER_OPEN = "open"
    LEAGUE_GENDER_WOMENS = "womens"
    LEAGUE_GENDER_CHOICES = (
        (LEAGUE_GENDER_CAPANDFILL, "Cap-and-Fill"),
        (LEAGUE_GENDER_COREC, "Co-Rec"),
        (LEAGUE_GENDER_MENS, "Men's"),
        (LEAGUE_GENDER_MIXED, "Mixed"),
        (LEAGUE_GENDER_OPEN, "Open"),
        (LEAGUE_GENDER_WOMENS, "Women's"),
    )

    LEAGUE_LEVEL_COMPETITIVE = "comp"
    LEAGUE_LEVEL_RECREATIONAL = "rec"
    LEAGUE_LEVEL_YOUTH = "youth"
    LEAGUE_LEVEL_CHOICES = (
        (LEAGUE_LEVEL_COMPETITIVE, "Competitive"),
        (LEAGUE_LEVEL_RECREATIONAL, "Recreational"),
        (LEAGUE_LEVEL_YOUTH, "Youth"),
    )

    LEAGUE_TYPE_EVENT = "event"
    LEAGUE_TYPE_LEAGUE = "league"
    LEAGUE_TYPE_TOURNAMENT = "tournament"
    LEAGUE_TYPE_CHOICES = (
        (LEAGUE_TYPE_EVENT, "Event"),
        (LEAGUE_TYPE_LEAGUE, "League"),
        (LEAGUE_TYPE_TOURNAMENT, "Tournament"),
    )

    year = models.IntegerField(help_text="four digit year, e.g. 2013")
    season = models.ForeignKey("leagues.Season")
    night = models.CharField(
        max_length=32,
        help_text='lower case, no special characters, e.g. "sunday", "tuesday and thursday", "end of season tournament"',
    )
    night_slug = models.SlugField()

    gender = models.CharField(max_length=32, choices=LEAGUE_GENDER_CHOICES)
    level = models.CharField(max_length=32, choices=LEAGUE_LEVEL_CHOICES)
    type = models.CharField(max_length=32, choices=LEAGUE_TYPE_CHOICES)

    tagline = models.TextField(
        blank=True,
        help_text="short tagline for description fields, e.g. SEO, Facebook, etc.",
    )
    summary_info = models.TextField(
        help_text="notes for league, e.g. 50-50 league format, showcase league notes"
    )
    detailed_info = models.TextField(help_text="details page text, use HTML")

    times = models.TextField(help_text="start to end time, e.g. 6:00-8:00pm")
    start_time = models.TimeField(null=True, help_text="start time for league")
    end_time = models.TimeField(null=True, help_text="end time for league")
    num_time_slots = models.IntegerField(default=1, help_text="number of time slots")

    schedule_note = models.TextField(
        blank=True, help_text="note to appear under the schedule"
    )
    captaining_note = models.TextField(
        blank=True,
        help_text="note for captaining, typically captain meeting date and time",
    )
    registration_prompt = models.TextField(
        blank=True,
        help_text="prompt to show during registration, e.g. to collect data around format preference",
    )

    num_games_per_week = models.IntegerField(
        default=1,
        help_text="number of games per week, used to calculate number of games for a league",
    )
    num_skip_weeks = models.IntegerField(
        default=0, help_text="number of weeks skipped, e.g. skipping 4th of July"
    )
    reg_start_date = models.DateTimeField(
        help_text="date and time that registration process is open (not currently automated)"
    )
    price_increase_start_date = models.DateTimeField(
        help_text="date and time when cost increases for league"
    )
    group_lock_start_date = models.DateTimeField(
        help_text="date and time that groups are locked"
    )
    waitlist_start_date = models.DateTimeField(
        help_text="date and time that waitlist is started (regardless of number of registrations)"
    )
    league_start_date = models.DateField(help_text="date of first game")
    league_end_date = models.DateField(help_text="date of last game")

    max_players = models.IntegerField(
        help_text="max players for league, extra registrations will be placed on waitlist"
    )
    baggage = models.IntegerField(help_text="max group size")
    min_age = models.IntegerField(help_text="minimum age (in years)", default=0)

    paypal_cost = models.IntegerField(
        help_text="base cost of league if paying by PayPal"
    )
    checks_accepted = models.BooleanField(default=True)
    check_cost_increase = models.IntegerField(
        help_text="amount to be added to paypal_cost if paying by check"
    )
    late_cost_increase = models.IntegerField(
        help_text="amount to be added to paypal_cost if paying after price_increase_start_date"
    )
    mail_check_address = models.TextField(help_text="treasurer mailing address")
    coupons_accepted = models.BooleanField(default=True)

    fields = models.ManyToManyField(
        Field,
        through="leagues.LeagueFields",
        help_text='Select the fields these games will be played at, use the green "+" icon if we\'re playing at a new field.',
    )

    division_email = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="email address for just this league",
    )
    division_email_group_id = models.CharField(max_length=128, blank=True, null=True)
    division_captains_email = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="email address for league captains",
    )
    division_captains_email_group_id = models.CharField(
        max_length=128, blank=True, null=True
    )

    state = models.CharField(
        max_length=32,
        choices=LEAGUE_STATE_CHOICES,
        help_text="state of league, changes whether registration is open or league is visible",
    )

    image_cover = models.ImageField(
        upload_to=generateLeagueCoverImagePath, blank=True, null=True
    )

    class Meta:
        db_table = "league"
        ordering = ["-year", "-season__order", "league_start_date"]

    def get_absolute_url(self):
        return reverse(
            "league_summary",
            kwargs={
                "year": self.year,
                "season": self.season.slug,
                "division": self.night_slug,
            },
        )

    def __str__(self):
        return "{} {} {}".format(self.season, self.year, self.night)

    def save(self):
        if not self.night_slug:
            self.night_slug = slugify(self.night)

        super(League, self).save()

    @property
    def display_gender(self):
        return dict(self.LEAGUE_GENDER_CHOICES)[self.gender]

    @property
    def display_level(self):
        return dict(self.LEAGUE_LEVEL_CHOICES)[self.level]

    @property
    def display_state(self):
        return dict(self.LEAGUE_STATE_CHOICES)[self.state]

    @property
    def display_type(self):
        return dict(self.LEAGUE_TYPE_CHOICES)[self.type]

    @property
    def night_title(self):
        return self.night.replace("_", " ")

    @property
    def season_title(self):
        return self.season.__str__().replace("_", " ")

    @property
    def season_year(self):
        return "{} {}".format(self.season, self.year)

    @property
    def gender_title(self):
        return self.gender.replace("_", " ")

    @property
    def league_start_datetime(self):
        start_time = time(0, 0, 0)
        if self.start_time:
            start_time = self.start_time

        return datetime.combine(self.league_start_date, start_time)

    @property
    def league_end_datetime(self):
        end_time = time(23, 59, 59)
        if self.end_time:
            end_time = self.end_time

        return datetime.combine(self.league_end_date, end_time)

    @property
    def paypal_price(self):
        if timezone.now() < self.price_increase_start_date:
            return self.paypal_cost

        return self.paypal_cost + self.late_cost_increase

    @property
    def check_price(self):
        if timezone.now() < self.price_increase_start_date:
            return self.paypal_cost + self.check_cost_increase

        return self.paypal_cost + self.check_cost_increase + self.late_cost_increase

    @property
    def is_cancelled(self):
        return self.state == self.LEAGUE_STATE_CANCELLED

    @property
    def is_closed(self):
        return self.state == self.LEAGUE_STATE_CLOSED

    @property
    def is_at_capacity(self):
        return len(self.get_complete_registrations()) >= self.max_players

    @property
    def is_after_registration_start(self):
        return timezone.now() >= self.reg_start_date

    @property
    def is_before_league_end(self):
        return timezone.now().date() <= self.league_end_date

    @property
    def is_after_price_increase(self):
        return timezone.now() >= self.price_increase_start_date

    @property
    def is_after_group_lock_start(self):
        return timezone.now() >= self.group_lock_start_date

    @property
    def is_after_waitlist_start(self):
        return timezone.now() >= self.waitlist_start_date

    def is_visible(self, user=None):
        if user and user.is_authenticated() and user.is_junta:
            return self.state in ["cancelled", "closed", "open", "preview"]

        return self.state in ["cancelled", "closed", "open"]

    @property
    def status_text(self):
        if self.is_cancelled:
            return "Cancelled"

        if timezone.now() < self.reg_start_date:
            return "Coming Soon"

        if timezone.now() < self.league_start_datetime:
            if (
                timezone.now() >= self.waitlist_start_date
                or len(self.get_complete_registrations()) >= self.max_players
            ):
                return "Waitlisting Registrations"
            else:
                return "Accepting Registrations"

        final_game = self.game_set.order_by("-date", "-start").first()

        if final_game and timezone.now().date() <= final_game.date:
            return "In Progress"
        elif timezone.now() <= self.league_end_datetime:
            return "In Progress"

        return "Completed"

    @property
    def status_color(self):
        if self.is_cancelled:
            return "#95a5a6"

        if timezone.now() < self.reg_start_date:
            return "#9b59b6"

        if timezone.now() < self.league_start_datetime:
            if (
                timezone.now() >= self.waitlist_start_date
                or len(self.get_complete_registrations()) >= self.max_players
            ):
                return "#f1c40f"
            else:
                return "#2ecc71"

        if timezone.now() <= self.league_end_datetime:
            return "#3498db"

        return "#95a5a6"

    def is_accepting_registrations(self, user=None):
        # admins and junta can register in preview mode
        if (
            user
            and user.is_authenticated()
            and user.is_junta
            and self.state in [self.LEAGUE_STATE_OPEN, self.LEAGUE_STATE_PREVIEW]
        ):
            return True

        # not state=open
        if self.state not in [self.LEAGUE_STATE_OPEN]:
            return False

        if not self.is_before_league_end:
            return False

        if not self.is_after_registration_start:
            return False

        return True

    def is_waitlisting_registrations(self, user=None):
        if not self.is_accepting_registrations(user):
            return False

        if self.is_after_waitlist_start:
            return True

        if self.is_at_capacity:
            return True

        return False

    def is_open(self, user=None):
        if (
            user
            and user.is_authenticated()
            and user.is_junta
            and self.state in ["open", "preview"]
        ):
            return True

        # if the user is not a league admin and the league is "open" and falls between valid dates
        return (
            self.state in ["open"]
            and self.is_after_registration_start
            and self.is_before_league_end
        )

    def get_visible_teams(self):
        return self.team_set.filter(hidden=False)

    def get_user_games(self, user):
        return self.game_set.filter(gameteams__team__teammember__user=user).order_by(
            "date"
        )

    def get_num_game_events(self):
        diff = self.league_end_date - self.league_start_date
        num_weeks = (diff.days / 7) + 1

        if self.num_games_per_week > 1:
            num_games = num_weeks * self.num_games_per_week

            if self.num_skip_weeks > 0:
                num_games = num_games - (self.num_skip_weeks * self.num_games_per_week)
        else:
            num_games = num_weeks

            if self.num_skip_weeks > 0:
                num_games = num_games - self.num_skip_weeks

        return floor(num_games)

    def get_captains(self):
        return get_user_model().objects.filter(
            teammember__team__league=self, teammember__captain=1
        )

    def get_captains_teammember(self):
        return TeamMember.objects.filter(team__league=self, captain=1).order_by("team")

    def player_survey_complete_for_user(self, user):
        return all(
            team.player_survey_complete(user)
            for team in Team.objects.filter(league=self, teammember__user=user)
        )

    def get_user_registration(self, user):
        user_registration = None

        if user and user.is_authenticated():
            try:
                return self.registrations_set.get(user=user)
            except ObjectDoesNotExist:
                pass

        return user_registration

    def get_registrations(self):
        return (
            self.registrations_set.order_by("registered", "updated", "created")
            .prefetch_related("baggage")
            .prefetch_related("league")
            .prefetch_related("user")
            .prefetch_related("user__profile")
        )

    def get_registrations_for_user(self, user):
        return self.get_registrations().filter(user=user).order_by("registered")

    def get_complete_registrations(self, registrations=None):
        if not registrations:
            registrations = self.get_registrations()

        return [
            r
            for r in registrations
            if r.is_complete and not r.waitlist and not r.refunded
        ]

    def get_waitlist_registrations(self, registrations=None):
        if not registrations:
            registrations = self.get_registrations()

        return [
            r for r in registrations if r.is_complete and r.waitlist and not r.refunded
        ]

    def get_incomplete_registrations(self, registrations=None):
        if not registrations:
            registrations = self.get_registrations()

        return [r for r in registrations if not r.is_complete and not r.refunded]

    def get_refunded_registrations(self, registrations=None):
        if not registrations:
            registrations = self.get_registrations()

        return [r for r in registrations if r.is_complete and r.refunded]

    def get_unassigned_registrations(self, registrations=None):
        team_member_users = [
            t.user
            for t in TeamMember.objects.filter(team__league=self).prefetch_related(
                "user"
            )
        ]

        if not registrations:
            registrations = self.get_registrations().exclude(user__in=team_member_users)

        return [r for r in registrations if r.is_complete and not r.refunded]

    def get_minor_registrations(self, registrations=None):
        if not registrations:
            registrations = self.get_complete_registrations()
        return [
            r
            for r in registrations
            if hasattr(r.user, "profile")
            and r.user.profile.is_minor(self.league_start_date)
        ]

    def get_player_count(self):
        if Team.objects.filter(league=self).exists():
            return TeamMember.objects.filter(team__league=self).count()

        return len(self.get_complete_registrations())

    def get_captain_count(self):
        return TeamMember.objects.filter(team__league=self, captain=True).count()

    def get_event_locations(self, games=None):
        if games is None:
            games = self.game_set.order_by(
                "date", "start", "field_name", "field_name__field"
            )

        locations = {}

        for game in games:
            game_field = game.field_name.field.pk
            game_field_name = game.field_name.pk
            location_id = "{}_{}".format(game_field, game_field_name)

            if location_id not in locations:
                locations[location_id] = {
                    "id": location_id,
                    "field": game.field_name.field,
                    "field_name": game.field_name,
                }

        locations = list(locations.values())
        locations.sort(key=lambda k: k["field"].name)
        locations.sort(key=lambda k: k["field_name"].name)

        return locations

    def get_game_locations(self, games=None):
        if games is None:
            games = self.game_set.order_by(
                "date", "start", "field_name", "field_name__field"
            )

        locations = {}

        for game in games:
            game_field = game.field_name.field.pk
            game_start = game.start.time() if game.start else game.start
            game_field_name = game.field_name.pk
            location_id = "{}_{}_{}".format(game_start, game_field, game_field_name)

            if location_id not in locations:
                locations[location_id] = {
                    "id": location_id,
                    "field": game.field_name.field,
                    "start": game.start.time() if game.start else None,
                    "field_name": game.field_name,
                }

        locations = list(locations.values())
        locations.sort(key=lambda k: k["field"].name)
        locations.sort(key=lambda k: k["field_name"].name)
        locations.sort(key=lambda k: k["start"])

        return locations

    def get_event_dates(self, games=None, event_locations=None):
        if games is None:
            games = self.game_set.order_by(
                "date", "start", "field_name", "field_name__field"
            )

        if event_locations is None:
            event_locations = self.get_event_locations()

        num_columns = len(event_locations)
        current_column_index = 0
        current_date = getattr(games.first(), "start", None)
        game_dates = {}
        game_dates[current_date] = []

        for game in games:
            if current_date != game.start:
                game_dates[game.start] = []

                while current_column_index < num_columns:
                    game_dates[current_date].append(None)
                    current_column_index += 1

                current_date = game.start
                current_column_index = 0

            game_field = game.field_name.field.pk
            game_start = game.start.time() if game.start else game.start
            game_field_name = game.field_name.pk
            column_id = "{}_{}".format(game_field, game_field_name)

            while event_locations[current_column_index]["id"] != column_id:
                game_dates[current_date].append(None)
                current_column_index += 1

            game_dates[current_date].append(game)
            current_column_index += 1

        game_dates = [{"date": i, "games": game_dates[i]} for i in sorted(game_dates)]

        for i, game_date in enumerate(game_dates):
            while len(game_dates[i]["games"]) < len(event_locations):
                game_dates[i]["games"].append(None)

        return game_dates

    def get_game_dates(self, games=None, game_locations=None):
        if games is None:
            games = self.game_set.order_by(
                "date", "start", "field_name", "field_name__field"
            )

        if game_locations is None:
            game_locations = self.get_game_locations()

        num_columns = len(game_locations)
        current_column_index = 0
        current_date = getattr(games.first(), "date", None)
        game_dates = {}
        game_dates[current_date] = []

        for game in games:
            if current_date != game.date:
                game_dates[game.date] = []

                while current_column_index < num_columns:
                    game_dates[current_date].append(None)
                    current_column_index += 1

                current_date = game.date
                current_column_index = 0

            game_field = game.field_name.field.pk
            game_start = game.start.time() if game.start else game.start
            game_field_name = game.field_name.pk
            column_id = "{}_{}_{}".format(game_start, game_field, game_field_name)

            while game_locations[current_column_index]["id"] != column_id:
                game_dates[current_date].append(None)
                current_column_index += 1

            game_dates[current_date].append(game)
            current_column_index += 1

        game_dates = [{"date": i, "games": game_dates[i]} for i in sorted(game_dates)]

        for i, game_date in enumerate(game_dates):
            while len(game_dates[i]["games"]) < len(game_locations):
                game_dates[i]["games"].append(None)

        return game_dates

    def sync_email_groups(self, force=False):
        division_email_success, division_email_address = self.sync_division_email_group(
            force
        )

        division_captains_email_success, division_captains_email_address = (
            self.sync_division_captains_email_group(force)
        )

        return (
            division_email_success,
            division_email_address,
            division_captains_email_success,
            division_captains_email_address,
        )

    def sync_division_email_group(self, force=False):
        group_address = generate_email_list_address(self)
        group_name = generate_email_list_name(self)

        from ultimate.utils.google_api import GoogleAppsApi

        api = GoogleAppsApi()
        group_id = api.prepare_group_for_sync(
            group_name=group_name,
            group_id=self.division_email_group_id,
            group_email_address=group_address,
            force=force,
        )

        self.division_email = group_address
        self.division_email_group_id = group_id

        success_count = 0

        if Team.objects.filter(league=self).exists():
            for team_member in TeamMember.objects.filter(team__league=self).order_by(
                "user__email"
            ):
                success_count += add_to_group(
                    group_email_address=group_address,
                    group_id=group_id,
                    email_address=team_member.user.email,
                )
        else:
            for registration in sorted(
                self.get_complete_registrations(), key=lambda r: r.user.email
            ):
                success_count += add_to_group(
                    group_email_address=group_address,
                    group_id=group_id,
                    email_address=registration.user.email,
                )

        self.save()

        return success_count, group_address

    def sync_division_captains_email_group(self, force=False):
        group_address = generate_email_list_address(self, suffix="captains")
        group_name = generate_email_list_name(self, suffix="Captains")

        from ultimate.utils.google_api import GoogleAppsApi

        api = GoogleAppsApi()
        group_id = api.prepare_group_for_sync(
            group_name=group_name,
            group_id=self.division_captains_email_group_id,
            group_email_address=group_address,
            force=force,
        )

        self.division_captains_email = group_address
        self.division_captains_email_group_id = group_id

        success_count = 0

        for team_member in TeamMember.objects.filter(
            team__league=self, captain=True
        ).order_by("user__last_name"):
            success_count += add_to_group(
                group_email_address=group_address,
                group_id=group_id,
                email_address=team_member.user.email,
            )

        self.save()

        return success_count, group_address


class LeagueFields(models.Model):
    id = models.AutoField(primary_key=True)
    league = models.ForeignKey("leagues.League")
    field = models.ForeignKey("leagues.Field")

    class Meta:
        db_table = "field_league"
        verbose_name_plural = "league fields"


class Baggage(models.Model):
    id = models.AutoField(primary_key=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = "baggage"

    def __str__(self):
        return "{} ({})".format(self.id, self.size)

    @property
    def size(self):
        return self.registrations_set.all().count()

    def get_registrations(self):
        return self.registrations_set.all()


class Registrations(models.Model):
    REGISTRATION_PAYMENT_CHOICES = (
        ("check", "Check"),
        ("paypal", "PayPal"),
    )

    # REGISTRATION_CAPTAIN_CHOICES = (
    #     (0, 'I refuse to captain.'),
    #     (1, 'I will captain if absolutely necessary.'),
    #     (2, 'I am willing to captain.'),
    #     (3, 'I would like to captain.'),
    #     (4, 'I will be very sad if I don\'t get to captain.'),
    # )

    REGISTRATION_CAPTAIN_CHOICES = (
        (0, "I do not want to captain"),
        (1, "I will captain"),
        (2, "I really want to captain this division"),
    )

    # 0 - I do not want to captain
    # 1 - I will captain (you should expect to be asked to captain!)
    # 2 - I really want to captain in this league! (you will be among the top considerations for captaining).

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    league = models.ForeignKey("leagues.League")
    baggage = models.ForeignKey("leagues.Baggage", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    registered = models.DateTimeField(null=True, blank=True, default=None)
    conduct_complete = models.BooleanField(default=False)
    waiver_complete = models.BooleanField(default=False)
    pay_type = models.CharField(
        choices=REGISTRATION_PAYMENT_CHOICES, max_length=6, null=True, blank=True
    )
    paypal_invoice_id = models.CharField(max_length=127, null=True, blank=True)
    paypal_complete = models.BooleanField(default=False)
    check_complete = models.BooleanField(default=False)
    payment_complete = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    waitlist = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    attendance = models.IntegerField(null=True, blank=True)
    captain = models.IntegerField(
        null=True, blank=True, choices=REGISTRATION_CAPTAIN_CHOICES
    )
    coupon = models.ForeignKey("leagues.Coupon", null=True, blank=True)
    prompt_response = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="response to the registration prompt for a division",
    )

    class Meta:
        db_table = "registrations"
        verbose_name_plural = "registrations"
        unique_together = (
            "user",
            "league",
        )
        ordering = ["-registered", "-updated", "-created"]

    def __str__(self):
        return "{} {} {} - {} {}".format(
            self.league.year,
            self.league.season,
            self.league.night,
            self.user,
            self.status,
        )

    @property
    def check_price(self):
        if self.coupon:
            return self.coupon.get_adjusted_price(
                self.league.check_price, self.league, self.user
            )

        return self.league.check_price

    @property
    def paypal_price(self):
        if self.coupon:
            return self.coupon.get_adjusted_price(
                self.league.paypal_price, self.league, self.user
            )

        return self.league.paypal_price

    @property
    def status(self):
        if self.refunded:
            return "Refunded"

        status = "Waiting for Conduct Waiver"
        if self.conduct_complete:
            status = "Waiting for Liability Waiver"
            if self.waiver_complete:
                status = "Waiting for Attendance Entry"
                if self.attendance is not None:
                    if self.pay_type == "check":
                        status = "Waiting for Check"
                    else:
                        status = "Waiting for Payment"
                    if (
                        self.check_complete
                        or self.paypal_complete
                        or self.payment_complete
                    ):
                        if self.waitlist:
                            status = "Complete (Waitlist)"
                        else:
                            status = "Complete"

        return status

    @property
    def progress(self):
        percentage = 0
        num_steps = 4

        if self.league.checks_accepted:
            num_steps = num_steps + 1

        interval = 100.0 / num_steps

        if self.conduct_complete:
            percentage += interval
            if self.waiver_complete:
                percentage += interval
                if self.attendance is not None:
                    percentage += interval

                    if self.league.checks_accepted and (
                        self.pay_type or self.payment_complete
                    ):
                        percentage += interval

                    if (
                        self.check_complete
                        or self.paypal_complete
                        or self.payment_complete
                    ):
                        percentage += interval

        return int(round(percentage))

    @property
    def is_ready_for_payment(self):
        if not self.conduct_complete:
            return False

        if not self.waiver_complete:
            return False

        if self.attendance is None:
            return False

        return True

    @property
    def is_complete(self):
        if not self.is_ready_for_payment:
            return False

        if (
            not self.check_complete
            and not self.paypal_complete
            and not self.payment_complete
        ):

            return False

        if self.refunded:
            return False

        return True

    @property
    def is_refunded(self):
        if not self.is_ready_for_payment:
            return False

        if (
            not self.check_complete
            and not self.paypal_complete
            and not self.payment_complete
        ):

            return False

        if not self.refunded:
            return False

        return True

    @property
    def baggage_size(self):
        if self.baggage:
            return self.baggage.size
        return 0

    @property
    def rating_adjusted(self):
        rating_total = self.user.rating_total
        num_events = self.league.get_num_game_events()
        absence_weight = rating_total / num_events

        return rating_total - ((self.attendance / 2) * absence_weight)

    def get_team_ids(self):
        try:
            return self.user.teammember_set.filter(
                team__league=self.league
            ).values_list("team__id", flat=True)
        except ObjectDoesNotExist:
            return None

    @atomic
    def add_to_baggage_group(self, email):
        if timezone.now() > self.league.group_lock_start_date:
            return (
                "You may not edit a group after the group change deadline ("
                + self.league.group_lock_start_date.strftime("%Y-%m-%d")
                + ")."
            )

        if self.user.email == email:
            return "You cannot form a group with yourself."

        if not self.is_complete:
            return "Your registration is currently incomplete and is ineligible to form groups."

        if self.waitlist:
            return (
                "You are currently on the waitlist and are ineligible to form groups."
            )

        try:
            registration = Registrations.objects.get(
                user__email=email, league=self.league
            )
        except ObjectDoesNotExist:
            return "No registration found for " + email + "."

        if not registration.is_complete:
            return (
                email
                + " has an incomplete registration and is ineligible to form groups."
            )

        if registration.waitlist:
            return (
                email
                + " is currently on the waitlist and is ineligible to form groups."
            )

        baggage_limit = self.league.baggage

        current_baggage = self.baggage
        current_baggage_registrations = current_baggage.get_registrations()

        target_baggage = registration.baggage

        if target_baggage == current_baggage:
            return email + " is already part of your group."

        if (
            current_baggage_registrations.count() + target_baggage.size
        ) > baggage_limit:
            return "Group with " + email + " exceeds limit."

        for current_baggage_registration in current_baggage_registrations:
            current_baggage_registration.baggage = target_baggage
            current_baggage_registration.save()

        current_baggage.delete()

        return True

    @atomic
    def leave_baggage_group(self):
        if timezone.now() >= self.league.group_lock_start_date:
            return (
                "You may not edit a group after the group change deadline ("
                + self.league.group_lock_start_date.strftime("%Y-%m-%d")
                + ")."
            )

        try:
            baggage = Baggage()
            baggage.save()

            if self.baggage.get_registrations().count() <= 1:
                self.baggage.delete()

            self.baggage = baggage
            self.save()

        except:
            return False

        return True


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, blank=True)
    color = models.CharField(max_length=96, blank=True)
    email = models.CharField(max_length=128, blank=True)
    league = models.ForeignKey("leagues.League")
    hidden = models.BooleanField(default=False)
    group_id = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = "team"

    def __str__(self):
        return self.pretty_name

    @property
    def pretty_name(self):
        name = "Team {}".format(self.id)

        if self.name:
            name = "{} - {}".format(name, self.name)
        if self.color:
            return "{} {}".format(name, self.color)

        return name

    @property
    def attendance_total(self):
        return sum(
            registration.attendance
            for registration in Registrations.objects.filter(
                league=self.league,
                user__id__in=self.teammember_set.all().values_list("user", flat=True),
            )
        )

    @property
    def attendance_average(self):
        if self.size > 0:
            return self.attendance_total / float(self.size)

        return 0

    @property
    def rating_total(self):
        return sum(
            team_member.user.rating_total for team_member in self.teammember_set.all()
        )

    @property
    def rating_average(self):
        if self.size > 0:
            return self.rating_total / float(self.size)

        return 0

    @property
    def rating_total_adjusted(self):
        return sum(
            registration.rating_adjusted
            for registration in Registrations.objects.filter(
                league=self.league,
                user__id__in=self.teammember_set.all().values_list("user", flat=True),
            )
        )

    @property
    def rating_average_adjusted(self):
        if self.size > 0:
            return self.rating_total_adjusted / float(self.size)

        return 0

    @property
    def size(self):
        return self.teammember_set.all().count()

    @property
    def css_background_color(self):
        color = "#95a5a6"
        if "black" in self.color.lower():
            color = "#34495e"
        if "blue" in self.color.lower():
            color = "#3498db"
        if "green" in self.color.lower():
            color = "#2ecc71"
        if "orange" in self.color.lower():
            color = "#e67e22"
        if "pink" in self.color.lower():
            color = "#ee6fa0"
        if "purple" in self.color.lower():
            color = "#9b59b6"
        if "red" in self.color.lower():
            color = "#e74c3c"
        if "yellow" in self.color.lower():
            color = "#f1c40f"
        if "white" in self.color.lower():
            color = "#ffffff"
        return color

    @property
    def css_background_color_dark(self):
        color = "#7f8c8d"
        if "black" in self.color.lower():
            color = "#2c3e50"
        if "blue" in self.color.lower():
            color = "#2980b9"
        if "green" in self.color.lower():
            color = "#27ae60"
        if "orange" in self.color.lower():
            color = "#d35400"
        if "pink" in self.color.lower():
            color = "#c7507e"
        if "purple" in self.color.lower():
            color = "#8e44ad"
        if "red" in self.color.lower():
            color = "#c0392b"
        if "yellow" in self.color.lower():
            color = "#d7ad04"
        if "white" in self.color.lower():
            color = "#f9f9f9"
        return color

    @property
    def css_text_color(self):
        color = "#ffffff"
        if "white" in self.color.lower():
            color = "#34495e"
        return color

    def contains_user(self, user):
        return self.teammember_set.filter(user=user).exists()

    def get_captains(self):
        return self.teammember_set.filter(captain=True)

    def get_members_with_baggage(self):
        return self.teammember_set.extra(
            select={
                "baggage_id": "SELECT baggage_id FROM registrations JOIN team ON team.league_id = registrations.league_id WHERE registrations.user_id = team_member.user_id AND team.id = team_member.team_id"
            }
        ).order_by("baggage_id")

    def get_members_count(self):
        return self.teammember_set.count()

    def get_male_members(self):
        return self.teammember_set.filter(user__profile__gender__iexact="M")

    def get_male_members_count(self):
        return self.get_male_members().count()

    def get_female_members(self):
        return self.teammember_set.filter(user__profile__gender__iexact="F")

    def get_female_members_count(self):
        return self.get_female_members().count()

    def get_past_games(self):
        return self.game_set.all().filter(date__lte=timezone.now().date())

    def get_record_list(self):
        # return in format {wins, losses, ties, conflicts}
        team_record = {
            "team_id": self.id,
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "conflicts": 0,
            "blanks": 0,
            "points_for": 0,
            "points_against": 0,
        }

        games = self.game_set.all()
        for game in games:

            team_reports = game.gamereport_set.filter(team=self)
            opponent_reports = game.gamereport_set.exclude(team=self)
            points_for = float(0)
            points_against = float(0)
            report_count = float(team_reports.count() + opponent_reports.count())

            team_result = 0
            for report in team_reports:
                team_score = report.gamereportscore_set.filter(team=self)[0].score
                opponent_score = report.gamereportscore_set.exclude(team=self)[0].score

                points_for += team_score
                points_against += opponent_score

                if team_score > opponent_score:
                    # team win
                    team_result = 1
                elif team_score < opponent_score:
                    # team loss
                    team_result = 2
                else:
                    # tie
                    team_result = 3

            opponent_result = 0
            for report in opponent_reports:
                team_score = report.gamereportscore_set.filter(team=self)[0].score
                opponent_score = report.gamereportscore_set.exclude(team=self)[0].score

                points_for += team_score
                points_against += opponent_score

                if team_score > opponent_score:
                    # win
                    opponent_result = 1
                elif team_score < opponent_score:
                    # loss
                    opponent_result = 2
                else:
                    # tie
                    opponent_result = 3

            if (
                (team_result == 1 and opponent_result == 1)
                or (team_result == 1 and opponent_result == 0)
                or (opponent_result == 1 and team_result == 0)
            ):

                team_record["wins"] += 1

            elif (
                (team_result == 2 and opponent_result == 2)
                or (team_result == 2 and opponent_result == 0)
                or (opponent_result == 2 and team_result == 0)
            ):

                team_record["losses"] += 1

            elif (
                (team_result == 3 and opponent_result == 3)
                or (team_result == 3 and opponent_result == 0)
                or (opponent_result == 3 and team_result == 0)
            ):

                team_record["ties"] += 1

            elif (
                team_result != opponent_result
                and team_result != 0
                and opponent_result != 0
            ):

                team_record["conflicts"] += 1

            else:

                team_record["blanks"] += 1

            if report_count > 1:
                points_for /= report_count
                points_against /= report_count

            team_record["points_for"] += points_for
            team_record["points_against"] += points_against

        return team_record

    def player_survey_complete(self, user):
        ratings_reports = self.playerratingsreport_set.annotate(
            num_ratings=Count("playerratings")
        ).filter(submitted_by=user)
        # since you don't rate yourself, looking for a rating report and teamsize - 1 rating entries
        return bool(ratings_reports.count() > 0) and bool(
            ratings_reports.filter(num_ratings__gte=self.size - 1).count() > 0
        )

    def sync_email_group(self, force=False):
        group_address = generate_email_list_address(self.league, team=self)
        group_name = generate_email_list_name(self.league, team=self)

        from ultimate.utils.google_api import GoogleAppsApi

        api = GoogleAppsApi()
        group_id = api.prepare_group_for_sync(
            group_name=group_name,
            group_id=self.group_id,
            group_email_address=group_address,
            force=force,
        )

        self.email = group_address
        self.group_id = group_id

        success_count = 0
        for team_member in self.teammember_set.all().order_by(
            "user__last_name", "user__first_name"
        ):
            success_count += add_to_group(
                group_email_address=group_address,
                group_id=group_id,
                email_address=team_member.user.email,
            )

        self.save()

        return success_count, group_address


class TeamMember(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey("leagues.Team")
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    captain = models.BooleanField(default=False)

    class Meta:
        db_table = "team_member"
        ordering = ["-captain", "user__last_name"]

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    @property
    def attendance_total(self):
        return Registrations.objects.get(
            league=self.team.league, user=self.user
        ).attendance

    @property
    def baggage(self):
        return Registrations.objects.get(
            league=self.team.league, user=self.user
        ).baggage


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    start = models.DateTimeField(null=True)
    field_name = models.ForeignKey("leagues.FieldNames")
    league = models.ForeignKey("leagues.league")
    teams = models.ManyToManyField("leagues.Team", through="leagues.GameTeams")

    class Meta:
        db_table = "game"
        ordering = ["-date", "field_name"]

    def __str__(self):
        return "{} {} {} {}".format(self.league, self.date, self.start, self.field_name)

    def get_teams(self):
        return self.teams.all()

    def get_display_teams(self):
        return self.teams.filter(hidden=False)

    def get_opposing_team(self, team):
        return self.teams.exclude(id=team.id).get()

    def get_user_opponent(self, user):
        try:
            return self.teams.exclude(teammember__user=user)[0:1].get()
        except ObjectDoesNotExist:
            return None

    def get_report_for_team(self, team):
        return self.gamereport_set.filter(team=team)

    def report_complete_for_team(self, user):
        return any(
            report.is_complete
            for report in self.gamereport_set.filter(
                team__teammember__user=user, team__teammember__captain=1
            )
        )

    def report_complete_for_user(self, user):
        return any(
            report.is_complete
            for report in self.gamereport_set.filter(
                last_updated_by=user,
                team__teammember__user=user,
                team__teammember__captain=1,
            )
        )


class GameTeams(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.ForeignKey("leagues.Game")
    team = models.ForeignKey("leagues.Team")

    class Meta:
        db_table = "game_teams"


class Coupon(models.Model):
    CODE_CHARACTERS = getattr(
        settings, "COUPON_CODE_CHARACTERS", "abcdefghijklmnopqrstuvwxyz"
    )
    CODE_SEGMENT_LENGTH = getattr(settings, "COUPON_CODE_SEGMENT_LENGTH", 4)
    CODE_SEGMENT_COUNT = getattr(settings, "COUPON_CODE_SEGMENT_COUNT", 3)

    COUPON_TYPE_FULL = "full"
    COUPON_TYPE_PERCENTAGE = "percentage"
    COUPON_TYPE_AMOUNT = "amount"
    COUPON_TYPE_CHOICES = (
        (COUPON_TYPE_FULL, "Full Value"),
        (COUPON_TYPE_PERCENTAGE, "Percentage"),
        (COUPON_TYPE_AMOUNT, "Amount"),
    )

    code = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        help_text="Leaving this field empty will generate a random code.",
    )

    type = models.CharField(max_length=20, choices=COUPON_TYPE_CHOICES)
    value = models.IntegerField(blank=True, null=True, default=None)

    use_count = models.IntegerField(
        default=0, help_text="How many times the coupon has been used"
    )
    use_limit = models.IntegerField(
        default=1, help_text="How many uses the coupon should have"
    )

    note = models.TextField(blank=True, help_text="What is the coupon for?")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid_until = models.DateTimeField(
        blank=True, null=True, help_text="Leave empty for coupons that never expire"
    )

    class Meta:
        db_table = "coupons"
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        super(Coupon, self).save(*args, **kwargs)

    @property
    def display_value(self):
        if self.type == self.COUPON_TYPE_AMOUNT:
            return "${} off".format(self.value)
        elif self.type == self.COUPON_TYPE_FULL:
            return "one free registration"
        elif self.type == self.COUPON_TYPE_PERCENTAGE:
            return "{}% off".format(self.value)

    def _generate_code(self):
        while 1:
            code = "-".join(
                "".join(
                    random.choice(self.CODE_CHARACTERS)
                    for i in range(self.CODE_SEGMENT_LENGTH)
                )
                for j in range(self.CODE_SEGMENT_COUNT)
            )
            try:
                Coupon.objects.get(code=code)
            except ObjectDoesNotExist:
                return code

    def get_adjusted_price(self, price, league=None, user=None):
        if not self.is_valid(league, user):
            return price

        if self.type == self.COUPON_TYPE_AMOUNT:
            return max(price - self.value, 0)
        elif self.type == self.COUPON_TYPE_FULL:
            return 0
        elif self.type == self.COUPON_TYPE_PERCENTAGE:
            return int(max(price * (1 - (self.value / 100.0)), 0))

    def is_valid(self, league=None, user=None):
        # if there is a use limit and uses have exceeded it
        if self.use_limit is not None and self.use_limit <= self.use_count:
            return False

        # if there is an expiration date and it today is past it
        if self.valid_until and self.valid_until < timezone.now():
            return False

        if league is not None:
            pass

        if user is not None:
            if self.couponredemtion_set.filter(redeemed_by=user).exists():
                return False

        return True

    def process(self, user):
        self.use_count = F("use_count") + 1
        self.save()
        coupon_redemption = CouponRedemtion.create(self, user)
        coupon_redemption.save()


class CouponRedemtion(models.Model):
    coupon = models.ForeignKey("leagues.Coupon")
    redeemed_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coupon_redemption"
        ordering = [
            "-redeemed_at",
            "redeemed_by",
        ]

    def __str__(self):
        return "{} by {} at {}".format(
            self.coupon.code, self.redeemed_by.email, self.redeemed_at
        )

    @classmethod
    def create(cls, coupon, user):
        coupon_redemption = cls(coupon=coupon, redeemed_by=user)
        return coupon_redemption
