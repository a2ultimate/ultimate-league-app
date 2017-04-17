from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from ultimate.forms import RegistrationAttendanceForm
from ultimate.leagues.models import *
from ultimate.middleware.http import Http403

from paypal.standard.forms import PayPalPaymentsForm


def index(request, year=None, season=None):
    if year and season:
        leagues = League.objects.filter(Q(year=year), Q(season__name=season) | Q(season__slug=season)).order_by('league_start_date')
    elif year:
        leagues = League.objects.filter(Q(year=year)).order_by('-league_start_date')
    else:
        leagues = League.objects.all().order_by('-league_start_date')

    if not request.user.is_superuser and not request.user.groups.filter(name='junta').exists():
        leagues = leagues.filter(state__in=['closed', 'open'])
    elif not request.user.is_superuser:
        leagues = leagues.filter(state__in=['closed', 'open', 'preview'])

    first_division = leagues.first()

    return render_to_response('leagues/index.html',
        {
            'leagues': leagues,
            'year': year,
            'season': season,

            'first_division': first_division,
        },
        context_instance=RequestContext(request))


def summary(request, year, season, division):
    league = get_object_or_404(League, Q(year=year), Q(season__name=season) | Q(season__slug=season), Q(night=division) | Q(night_slug=division))
    return render_to_response('leagues/summary.html',
        {
            'league': league
        },
        context_instance=RequestContext(request))


def details(request, year, season, division):
    league = get_object_or_404(League, Q(year=year), Q(season__name=season) | Q(season__slug=season), Q(night=division) | Q(night_slug=division))
    return render_to_response('leagues/details.html',
        {
            'league': league
        },
        context_instance=RequestContext(request))


def players(request, year, season, division):
    league = get_object_or_404(League, Q(year=year), Q(season__name=season) | Q(season__slug=season), Q(night=division) | Q(night_slug=division))

    user_registration = None
    if request.user.is_authenticated():
        try:
            user_registration = Registrations.objects.get(user=request.user, league=league)
        except ObjectDoesNotExist:
            user_registration = None

    complete_registrations = league.get_complete_registrations()
    incomplete_registrations = league.get_incomplete_registrations()
    waitlist_registrations = league.get_waitlist_registrations()
    refunded_registrations = league.get_refunded_registrations()
    unassigned_registrations = league.get_unassigned_registrations()

    return render_to_response('leagues/players.html',
        {
            'league': league,
            'user_registration': user_registration,
            'complete_registrations': complete_registrations,
            'incomplete_registrations': incomplete_registrations,
            'waitlist_registrations': waitlist_registrations,
            'refunded_registrations': refunded_registrations,
            'unassigned_registrations': unassigned_registrations,

            'registrations_female': len([r for r in complete_registrations if hasattr(r.user, 'profile') and r.user.profile.is_female()]),
            'registrations_male': len([r for r in complete_registrations if hasattr(r.user, 'profile') and r.user.profile.is_male()]),
            'registrations_minor': len([r for r in complete_registrations if hasattr(r.user, 'profile') and r.user.profile.is_minor(league.league_start_date)]),
            'registrations_remaining': max(0, league.max_players - len(complete_registrations)),
        },
        context_instance=RequestContext(request))


def teams(request, year, season, division):
    league = get_object_or_404(League, Q(year=year), Q(season__name=season) | Q(season__slug=season), Q(night=division) | Q(night_slug=division))
    user_games = None

    games = league.game_set.order_by('date', 'start', 'field_name', 'field_name__field')
    game_locations = league.get_game_locations(games=games)
    game_dates = league.get_game_dates(games=games, game_locations=game_locations)

    next_game_date = getattr(games.filter(date__gte=timezone.now().date()).first(), 'date', None)

    if request.user.is_authenticated():
        user_games = games.filter(league=league, gameteams__team__teammember__user=request.user).order_by('date')

    return render_to_response('leagues/teams.html',
        {
            'league': league,

            'next_game_date': next_game_date,
            'user_games': user_games,

            'game_locations': game_locations,
            'game_dates': game_dates,

            'teams': Team.objects.filter(league=league, hidden=False)
                         .prefetch_related('teammember_set')
                         .prefetch_related('teammember_set__user')
                         .prefetch_related('teammember_set__user__profile'),
        },
        context_instance=RequestContext(request))


@atomic
@login_required
def group(request, year, season, division):
    league = get_object_or_404(League, Q(year=year), Q(season__name=season) | Q(season__slug=season), Q(night=division) | Q(night_slug=division))
    registration = get_object_or_404(Registrations, league=league, user=request.user)

    if request.method == 'POST':
        if 'leave_group' in request.POST:
            message = registration.leave_baggage_group()
            if message is True:
                messages.success(request, 'You were successfully removed from your baggage group.')
            elif isinstance(message, str):
                messages.error(request, message)
            else:
                messages.error(request, 'You could not be removed from your baggage group.')

        elif 'add_group' in request.POST and 'email' in request.POST:
            email = request.POST.get('email')
            message = registration.add_to_baggage_group(email)
            if message is True:
                messages.success(request, 'You were successfully added to ' + email + '\'s group.')
            else:
                messages.error(request, message)

        return HttpResponseRedirect(reverse('league_group', kwargs={'year': year, 'season': season, 'division': division}))

    return render_to_response('leagues/group.html',
        {
            'league': league,
            'registration': registration
        },
        context_instance=RequestContext(request))


@atomic
@login_required
def registration(request, year, season, division, section=None):
    league = get_object_or_404(League, Q(year=year), Q(season__name=season) | Q(season__slug=season), Q(night=division) | Q(night_slug=division))

    try:
        registration, created = Registrations.objects.get_or_create(user=request.user, league=league)
    except IntegrityError:
        registration = Registrations.objects.get(user=request.user, league=league)

    if not league.is_open(request.user):
        return render_to_response('leagues/registration/error.html', {
                'league': league,
                'registration': registration,
                'errors': ['closed'],
            },
            context_instance=RequestContext(request))

    if not registration.is_complete:
        errors = []
        try:
            user_profile = request.user.profile
            if league.min_age:
                if not user_profile or \
                        user_profile.get_age_on(league.league_start_date) < league.min_age:
                    errors.append('age')

            if not user_profile or not user_profile.is_complete_for_user:
                errors.append('profile')

            if not request.user.has_completed_player_rating:
                errors.append('rating')

            if request.user.has_expired_player_rating:
                errors.append('rating_expired')

        except ObjectDoesNotExist:
            errors.append('unknown')

        if len(errors):
            return render_to_response('leagues/registration/error.html',
                {
                    'league': league,
                    'registration': registration,
                    'errors': errors,
                },
                context_instance=RequestContext(request))

    num_steps = 4
    if league.checks_accepted:
        num_steps = num_steps + 1

    tick_percentage = 100.0 / num_steps

    attendance_form = None
    paypal_form = None

    if request.method == 'POST':
        success = True

        # conduct response
        if 'conduct_accept' in request.POST:
            registration.conduct_complete = 1
            registration.save()
            messages.success(request, 'Code of conduct response saved.')
        elif 'conduct_decline' in request.POST:
            registration.conduct_complete = 0
            registration.save()
            success = False
            section = 'conduct'
            messages.error(request, 'You must accept the code of conduct to continue.')

        # waiver response
        if 'waiver_accept' in request.POST:
            registration.waiver_complete = 1
            registration.save()
            messages.success(request, 'Waiver response saved.')
        elif 'waiver_decline' in request.POST:
            registration.waiver_complete = 0
            registration.save()
            success = False
            section = 'waiver'
            messages.error(request, 'You must accept the waiver to continue.')

        # attendance/captaining response
        if 'id' in request.POST and 'attendance' in request.POST:
            attendance_form = RegistrationAttendanceForm(request.POST, instance=registration)
            if attendance_form.is_valid():
                attendance_form.save()

                if not registration.baggage_id:
                    baggage = Baggage()
                    baggage.save()
                    registration.baggage_id = baggage.id
                    registration.save()

                if league.check_price == 0 and league.paypal_price == 0:
                    registration.registered = timezone.now()
                    registration.save()

                if league.type == 'league':
                    messages.success(request, 'Attendance and captaining response saved.')
                else:
                    messages.success(request, 'Attendance response saved.')

            else:
                success = False
                section = 'attendance'

                if league.type == 'league':
                    messages.error(request, 'You must provide a valid attendance and captaining rating to continue.')
                else:
                    messages.error(request, 'You must provide a valid attendance rating to continue.')

        # payment type response
        if 'pay_type' in request.POST:
            if not league.checks_accepted:
                registration.pay_type = 'paypal'
                registration.save()
                messages.error(request, 'Payment type set to PayPal. Checks are not accepted for this league.')

            elif request.POST.get('pay_type').lower() == 'pay with check':
                registration.pay_type = 'check'
                registration.save()
                messages.success(request, 'Payment type set to check.')

            elif request.POST.get('pay_type').lower() == 'pay with paypal':
                registration.pay_type = 'paypal'
                registration.save()
                messages.success(request, 'Payment type set to PayPal.')

            else:
                success = False
                section = 'pay_type'
                messages.error(request, 'You must select a valid payment type to continue.')

        if 'coupon_code' in request.POST:
            if league.coupons_accepted:
                try:
                    coupon = Coupon.objects.get(code=request.POST.get('coupon_code'))
                except ObjectDoesNotExist:
                    coupon = None

                if coupon and coupon.is_valid():
                    registration.coupon = coupon
                    registration.save()

                    registration.coupon.use_count = F('use_count') + 1
                    registration.coupon.save()

                    messages.success(request, 'Your coupon code has been applied.')
                else:
                    success = False
                    messages.error(request, 'You have entered an invalid coupon code.')
            else:
                success = False
                messages.error(request, 'Coupon codes are not accepted for this division.')

        if 'remove_coupon' in request.POST:
            if registration.coupon:
                registration.coupon.use_count = F('use_count') - 1
                registration.coupon.save()

                registration.coupon = None
                registration.save()

                messages.success(request, 'Your coupon has been removed and will not be used with this registration.')
            else:
                success = False
                messages.error(request, 'No coupon has been added to this registration.')

        if 'process_registration' in request.POST:
            if registration.is_ready_for_payment:
                registration.payment_complete = True
                registration.registered = timezone.now()
                registration.save()

                success = True
                messages.success(request, 'Your registration has been processed.')

            else:
                messages.error(request, 'Your registration could not be processed.')

        if success:
            return HttpResponseRedirect(reverse('league_registration', kwargs={'year': year, 'season': season, 'division': division}))

    if section == 'conduct' or not registration.conduct_complete:
        return render_to_response('leagues/registration/conduct.html',
            {
                'league': league,
                'registration': registration,
                'section': 'conduct',
                'tick_percentage': tick_percentage
            },
            context_instance=RequestContext(request))

    if section == 'waiver' or not registration.waiver_complete:
        return render_to_response('leagues/registration/waiver.html',
            {
                'league': league,
                'registration': registration,
                'section': 'waiver',
                'tick_percentage': tick_percentage
            },
            context_instance=RequestContext(request))

    if section == 'attendance' or \
            registration.attendance is None or \
            (registration.captain is None and league.type == 'league'):

        if not attendance_form:
            attendance_form = RegistrationAttendanceForm(instance=registration)

        return render_to_response('leagues/registration/attendance.html',
            {
                'league': league,
                'registration': registration,
                'attendance_form': attendance_form,
                'section': 'attendance',
                'tick_percentage': tick_percentage
            },
            context_instance=RequestContext(request))

    if registration.check_price > 0 or registration.paypal_price > 0:

        if league.checks_accepted and (section == 'pay_type' or not registration.pay_type or (registration.pay_type != 'check' and registration.pay_type != 'paypal')):

            return render_to_response('leagues/registration/payment.html',
                {
                    'league': league,
                    'registration': registration,
                    'section': 'pay_type',
                    'tick_percentage': tick_percentage
                },
                context_instance=RequestContext(request))

        if not registration.paypal_invoice_id:
            registration.paypal_invoice_id = str(uuid.uuid4())
            registration.save()

        if not registration.paypal_complete and not registration.check_complete:
            baseUrl = request.build_absolute_uri(getattr(settings, 'FORCE_SCRIPT_NAME', '/')).replace(request.path_info.replace(' ', '%20'), '')

            paypal_dict = {
                'amount': registration.paypal_price,
                'cancel_return': '{}/leagues/{}/{}/{}/registration/'.format(baseUrl, league.year, league.season.slug, league.night_slug),
                'invoice': registration.paypal_invoice_id,
                'item_name': '{} {} {}'.format(league.season_title, league.year, league.night_title),
                'notify_url': '{}/leagues/registration/payment/{}'.format(baseUrl, getattr(settings, 'PAYPAL_CALLBACK_SECRET', 'notification/callback/for/a2ultimate/secret/')),
                'return_url': '{}/leagues/{}/{}/{}/registration-complete/'.format(baseUrl, league.year, league.season.slug, league.night_slug),
            }

            paypal_form = PayPalPaymentsForm(initial=paypal_dict)
            # https://ppmts.custhelp.com/app/answers/detail/a_id/165

    return render_to_response('leagues/registration/status.html',
        {
            'paypal_form': paypal_form,
            'league': league,
            'registration': registration,
            'section': 'status',
            'tick_percentage': tick_percentage
        },
        context_instance=RequestContext(request))


@csrf_exempt
def registrationcomplete(request, year, season, division):
    return redirect('league_registration', year=year, season=season, division=division)
