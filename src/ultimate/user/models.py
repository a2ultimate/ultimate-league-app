from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    """
    Custom manager for User.
    """

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        is_active = extra_fields.pop('is_active', True)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=is_active,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        is_staff = extra_fields.pop('is_staff', False)
        return self._create_user(email, password, is_staff, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class AbstractUser(AbstractBaseUser, PermissionsMixin):

    """Abstract User with the same behaviour as Django's default User.
    AbstractUser does not have username field. Uses email as the
    USERNAME_FIELD for authentication.
    Use this if you need to extend User.
    Inherits from both the AbstractBaseUser and PermissionMixin.
    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser
    """

    email = models.EmailField(_('email address'), max_length=255,
                              unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False, help_text=_(
            'Designates whether the user can log into the admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_(
        'Designates whether this user should be treated as '
        'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    NOT_SUBMITTED_FIELDS = ['first_name', 'last_name', ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_junta(self):
        return self.is_superuser or self.groups.filter(name='junta').exists()


class User(AbstractUser):

    """
    Concrete class of AbstractUser.
    Use this if you don't need to extend User.
    """

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    @property
    def has_completed_player_rating(self):
        return self.playerratings_set.filter(submitted_by=self, user=self).exists()

    @property
    def has_expired_player_rating(self):
        expiration_months = getattr(settings, 'A2U_RATING_EXPIRATION_MONTHS', 0)

        if expiration_months == 0:
            return False

        return not self.playerratings_set.filter(submitted_by=self, user=self,
            updated__gte=timezone.now() - relativedelta(months=expiration_months)).exists()

    @property
    def rating_totals(self):
        player_ratings_collected = {'athleticism': [],
                                    'experience': [],
                                    'spirit': [],
                                    'strategy': [],
                                    'throwing': []}

        ratings = self.playerratings_set.all()

        rating_limit = getattr(settings, 'A2U_RATING_LIMIT_MONTHS', 0)
        if rating_limit:
            ratings = ratings.filter(Q(ratings_type=PlayerRatings.RATING_TYPE_USER) |
                Q(ratings_type=PlayerRatings.RATING_TYPE_JUNTA) |
                Q(updated__gte=timezone.now() - relativedelta(months=rating_limit)))

        for rating in ratings:
            if rating.athleticism:
                player_ratings_collected['athleticism'].append(rating.athleticism)
            if rating.experience:
                player_ratings_collected['experience'].append(rating.experience)
            if rating.spirit:
                player_ratings_collected['spirit'].append(rating.spirit)
            if rating.strategy:
                player_ratings_collected['strategy'].append(rating.strategy)
            if rating.throwing:
                player_ratings_collected['throwing'].append(rating.throwing)

        player_ratings_averaged = {}
        for key, values in list(player_ratings_collected.items()):
            player_ratings_averaged[key] = 1

            if len(values):
                player_ratings_averaged[key] = float(sum(values)) / len(values)

        def calculate_weighted_athleticism_rating(rating, max_rating, percentage):
            # 0.1x^3 - 1.2x^2 + 5x
            rating = (0.1 * pow(rating, 3)) + (-1.2 * pow(rating, 2)) + (5 * rating)
            max_rating = (0.1 * pow(max_rating, 3)) + (-1.2 * pow(max_rating, 2)) + (5 * max_rating)
            rating = rating / max_rating * percentage
            return rating

        def calculate_weighted_experience_rating(rating, max_rating, percentage):
            # x^1.4
            rating = pow(rating, 1.4)
            max_rating = pow(max_rating, 1.4)
            rating = rating / max_rating * percentage
            return rating

        def calculate_weighted_spirit_rating(rating, max_rating, percentage):
            # x
            rating = int(rating / max_rating * percentage)
            return rating

        def calculate_weighted_strategy_rating(rating, max_rating, percentage):
            # x^0.25
            rating = pow(rating, 0.25)
            max_rating = pow(max_rating, 0.25)
            rating = rating / max_rating * percentage
            return rating

        def calculate_weighted_throwing_rating(rating, max_rating, percentage):
            # 0.1x^3 - 1.2x^2 + 5x
            rating = (0.1 * pow(rating, 3)) + (-1.2 * pow(rating, 2)) + (5 * rating)
            max_rating = (0.1 * pow(max_rating, 3)) + (-1.2 * pow(max_rating, 2)) + (5 * max_rating)
            rating = rating / max_rating * percentage
            return rating

        player_ratings_averaged['athleticism'] -= 3
        player_ratings_averaged['throwing'] -= 3

        player_ratings_weighted = {}
        player_ratings_weighted['athleticism'] = calculate_weighted_athleticism_rating(player_ratings_averaged['athleticism'], 3, 32)
        player_ratings_weighted['experience'] = calculate_weighted_experience_rating(player_ratings_averaged['experience'], 6, 18)
        player_ratings_weighted['strategy'] = calculate_weighted_strategy_rating(player_ratings_averaged['strategy'], 6, 18)
        player_ratings_weighted['throwing'] = calculate_weighted_throwing_rating(player_ratings_averaged['throwing'], 3, 32)

        # rating cannot be less than 0
        player_ratings_weighted['total'] = max(sum(player_ratings_weighted.values()), 0)

        # spirt is calculated after total because spirit is not included in that calculation
        player_ratings_weighted['spirit'] = calculate_weighted_spirit_rating(player_ratings_averaged['spirit'], 10, 100)

        return player_ratings_weighted

    @property
    def rating_total(self):
        return self.rating_totals['total']

    @property
    def self_rating(self):
        return self.playerratings_set.filter(ratings_type=PlayerRatings.RATING_TYPE_USER).first()

    def concussion_waiver(self, now=None):
        if not now:
            now = timezone.now().date()

        if self.profile.get_age_on(now) > 18:
            return False

        return self.player_concussion_waiver_submitted_by_set.first()

    def concussion_waiver_status(self):
        waiver = self.concussion_waiver()
        status_choices = dict(PlayerConcussionWaiver.PLAYER_CONCUSSION_WAIVER_CHOICES)
        if waiver:
            return status_choices[waiver.status]

        return status_choices[PlayerConcussionWaiver.PLAYER_CONCUSSION_WAIVER_NOT_SUBMITTED]


class Player(models.Model):
    GENDER_FEMALE = 'F'
    GENDER_MALE = 'M'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Man'),
        (GENDER_FEMALE, 'Woman'),
    )

    JERSEY_SIZE_CHOICES = (
        ('XS', 'XS - Extra Small'),
        ('S', 'S - Small'),
        ('M', 'M - Medium'),
        ('L', 'L - Large'),
        ('XL', 'XL -Extra Large'),
        ('XXL', 'XXL - Extra Extra Large'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    groups = models.TextField()
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    personal_pronoun = models.TextField(blank=True)
    nickname = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    zip_code = models.CharField(max_length=15, blank=True)
    height_inches = models.IntegerField(default=0, blank=True, null=True)
    highest_level = models.TextField(blank=True)
    jersey_size = models.CharField(max_length=45, choices=JERSEY_SIZE_CHOICES, blank=True)

    guardian_name = models.TextField(blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_phone = models.TextField(blank=True)

    @property
    def age(self):
        return self.get_age_on(timezone.now().date())

    @property
    def is_complete_for_user(self):
        is_complete = bool(self.gender and self.date_of_birth)

        if is_complete and self.age < 18:
            is_complete = bool(is_complete and self.guardian_name and self.guardian_email and self.guardian_phone)

        return is_complete

    @property
    def matching_preference(self):
        return dict(self.GENDER_CHOICES)[self.gender]

    def is_male(self):
        return self.gender == self.GENDER_MALE

    def is_female(self):
        return self.gender == self.GENDER_FEMALE

    def is_minor(self, now=None):
        if not now:
            now = timezone.now().date()

        return self.get_age_on(now) < 18

    def get_age_on(self, now):
        if not self.date_of_birth:
            return 0

        return (now.year - self.date_of_birth.year) - int((now.month, now.day) < (self.date_of_birth.month, self.date_of_birth.day))


class PlayerRatings(models.Model):
    RATING_EXPERIENCE_CHOICES = (
        (1, 'I am new to ultimate or have played less than 2 years of pickup.'),
        (2, 'I have played in an organized league or on a high school team for 1-2 seasons, or pickup for 3+ years.'),
        (3, 'I have played in an organized league or on a high school team for 3+ seasons.'),
        (4, 'I have played on a college or club team in the last 6 years.'),
        (5, 'I have played multiple seasons on a college or club team in the last 4 years.'),
        (6, 'I have played multiple seasons on a regionals or nationals-level college or club team in the last 4 years.'),
    )

    RATING_STRATEGY_CHOICES = (
        (1, 'I am new to organized ultimate.'),
        (2, 'I have basic knowledge of the game (e.g. stall counts, pivoting).'),
        (3, 'I have moderate knowledge (e.g. vertical stack, force, basic man defense).'),
        (4, 'I have advanced knowledge (e.g. zone defense, horizontal stack, switching).'),
        (5, 'I am familiar enough with the above concepts that I could explain them to a new player.'),
        (6, 'I would consider myself an expert in ultimate strategy.'),
    )

    RATING_THROWING_CHOICES = (
        (1, 'I am a novice or am learning to throw.'),
        (2, 'I can throw a backhand 10 yards with 90% confidence.'),
        (3, 'I can throw a forehand 10+ yards with 90% confidence and can handle if needed.'),
        (4, 'I am confident throwing forehand and backhand various distances and can handle at a league level.'),
        (5, 'I am confident throwing break throws and can be a very good league-level handler.'),
        (6, 'I am confident in many styles of throws and could be a college or club-level handler.'),
    )

    RATING_ATHLETICISM_CHOICES = (
        (1, 'I am slow, it is hard to change direction, and am easily winded.'),
        (2, 'I can change direction decently, but need to rest often.'),
        (3, 'I am somewhat fast, can make hard cuts, and can play for a few minutes at a time before resting.'),
        (4, 'I am fairly fast, can change direction and react well, and can play a few hard points in a row.'),
        (5, 'I am very fast, can turn well, jump high, and need little rest.'),
        (6, 'I am faster than anyone on the field at any level and enjoy playing almost every point.'),
    )

    RATING_COMPETITIVENESS_CHOICES = (
        (1, 'I do not care whether I win or lose, I play purely to socialize and have fun.'),
        (2, 'I play ultimate to have fun, but would prefer to win.'),
        (3, 'I am competitive, fight to win close games, and am somewhat disappointed by a loss.'),
        (4, 'I am extremely competitive and am very disappointed by a loss.'),
    )

    RATING_TYPE_CAPTAIN = 1
    RATING_TYPE_JUNTA = 2
    RATING_TYPE_USER = 3
    RATING_TYPE = (
        (RATING_TYPE_CAPTAIN, 'Captain'),
        (RATING_TYPE_JUNTA, 'Junta'),
        (RATING_TYPE_USER, 'User'),
    )

    id = models.AutoField(primary_key=True)

    experience = models.PositiveIntegerField(
        default=None, choices=RATING_EXPERIENCE_CHOICES, blank=True, null=True)
    strategy = models.PositiveIntegerField(
        default=None, choices=RATING_STRATEGY_CHOICES, blank=True, null=True)
    throwing = models.PositiveIntegerField(
        default=None, choices=RATING_THROWING_CHOICES, blank=True, null=True)
    athleticism = models.PositiveIntegerField(
        default=None, choices=RATING_ATHLETICISM_CHOICES, blank=True, null=True)
    competitiveness = models.PositiveIntegerField(
        default=None, choices=RATING_COMPETITIVENESS_CHOICES, blank=True, null=True)
    spirit = models.PositiveIntegerField(default=None, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='ratings_submitted_by_set')
    ratings_type = models.PositiveIntegerField(choices=RATING_TYPE)
    ratings_report = models.ForeignKey(
        'user.PlayerRatingsReport', blank=True, null=True)
    not_sure = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'player ratings'

    def save(self, *args, **kwargs):
        if not self.experience:
            self.experience = None
        if not self.strategy:
            self.strategy = None
        if not self.throwing:
            self.throwing = None
        if not self.athleticism:
            self.athleticism = None
        if not self.competitiveness:
            self.competitiveness = None
        if not self.spirit:
            self.spirit = None
        super(PlayerRatings, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {} <- {}'.format(str(self.updated), self.user, self.submitted_by)


class PlayerRatingsReport(models.Model):
    id = models.AutoField(primary_key=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='ratings_report_submitted_by_set')
    team = models.ForeignKey('leagues.Team')
    updated = models.DateTimeField()

    def __str__(self):
        return '{}, {}, {}'.format(self.team, self.team.league, self.submitted_by)


class PlayerConcussionWaiver(models.Model):
    PLAYER_CONCUSSION_WAIVER_NOT_SUBMITTED = 'not_submitted'
    PLAYER_CONCUSSION_WAIVER_SUBMITTED = 'submitted'
    PLAYER_CONCUSSION_WAIVER_APPROVED = 'approved'
    PLAYER_CONCUSSION_WAIVER_DENIED = 'denied'
    PLAYER_CONCUSSION_WAIVER_CHOICES = (
        (PLAYER_CONCUSSION_WAIVER_NOT_SUBMITTED, 'Not Submitted'),
        (PLAYER_CONCUSSION_WAIVER_SUBMITTED, 'Submitted'),
        (PLAYER_CONCUSSION_WAIVER_APPROVED, 'Approved'),
        (PLAYER_CONCUSSION_WAIVER_DENIED, 'Denied'),
    )

    id = models.AutoField(primary_key=True)

    file = models.FileField(upload_to='concussion_waivers/%Y/%m/%d/', blank=True, null=True)

    status = models.CharField(max_length=32, choices=PLAYER_CONCUSSION_WAIVER_CHOICES, default=PLAYER_CONCUSSION_WAIVER_NOT_SUBMITTED)

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='player_concussion_waiver_submitted_by_set')
    submitted_at = models.DateTimeField(blank=True, null=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='player_concussion_waiver_reviewed_by_set', blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.submitted_by, self.status)
