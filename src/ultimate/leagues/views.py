import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist, Q
from django.db.transaction import atomic
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from ultimate.forms import RegistrationAttendanceForm
from ultimate.leagues.models import Baggage, Coupon, League, Registrations, Team

from paypal.standard.forms import PayPalPaymentsForm


def index(request, year=None, season=None):
    if year and season:
        leagues = League.objects.filter(Q(year=year), Q(season__name=season) | Q(season__slug=season)).order_by('league_start_date')
    elif year:
        leagues = League.objects.filter(Q(year=year)).order_by('-league_start_date')
    else:
        leagues = League.objects.all().order_by('-league_start_date')

    if not request.user.is_superuser and not request.user.groups.filter(name='junta').exists():
        leagues = leagues.filter(state__in=['cancelled', 'closed', 'open'])

    if not leagues:
        raise Http404('Season Not Found')

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
    valid_division_states = ['cancelled', 'closed', 'open']
    if request.user.is_superuser or request.user.groups.filter(name='junta').exists():
        valid_division_states = valid_division_states + ['hidden', 'preview']

    try:
        league = League.objects.get(
            Q(year=year),
            Q(season__name=season) | Q(season__slug=season),
            Q(night=division) | Q(night_slug=division),
            state__in=valid_division_states,
        )
    except League.DoesNotExist:
        raise Http404('Division Not Found')

    return render_to_response('leagues/summary.html',
        {
            'league': league
        },
        context_instance=RequestContext(request))


def details(request, year, season, division):
    valid_division_states = ['cancelled', 'closed', 'open']
    if request.user.is_superuser or request.user.groups.filter(name='junta').exists():
        valid_division_states = valid_division_states + ['hidden', 'preview']

    try:
        league = League.objects.get(
            Q(year=year),
            Q(season__name=season) | Q(season__slug=season),
            Q(night=division) | Q(night_slug=division),
            state__in=valid_division_states,
        )
    except League.DoesNotExist:
        raise Http404('Division Not Found')

    return render_to_response('leagues/details.html',
        {
            'league': league
        },
        context_instance=RequestContext(request))


def players(request, year, season, division):
    valid_division_states = ['cancelled', 'closed', 'open']
    if request.user.is_superuser or request.user.groups.filter(name='junta').exists():
        valid_division_states = valid_division_states + ['hidden', 'preview']

    try:
        league = League.objects.get(
            Q(year=year),
            Q(season__name=season) | Q(season__slug=season),
            Q(night=division) | Q(night_slug=division),
            state__in=valid_division_states,
        )
    except League.DoesNotExist:
        raise Http404('Division Not Found')

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

            'num_registrations_female': len([r for r in complete_registrations if hasattr(r.user, 'profile') and r.user.profile.is_female()]),
            'num_registrations_male': len([r for r in complete_registrations if hasattr(r.user, 'profile') and r.user.profile.is_male()]),
            'num_registrations_minor': len([r for r in complete_registrations if hasattr(r.user, 'profile') and r.user.profile.is_minor(league.league_start_date)]),
            'num_registrations_remaining': max(0, league.max_players - len(complete_registrations)),
        },
        context_instance=RequestContext(request))


def teams(request, year, season, division):
    valid_division_states = ['cancelled', 'closed', 'open']
    if request.user.is_superuser or request.user.groups.filter(name='junta').exists():
        valid_division_states = valid_division_states + ['hidden', 'preview']

    try:
        league = League.objects.get(
            Q(year=year),
            Q(season__name=season) | Q(season__slug=season),
            Q(night=division) | Q(night_slug=division),
            state__in=valid_division_states,
        )
    except League.DoesNotExist:
        raise Http404('Division Not Found')

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
    valid_division_states = ['cancelled', 'closed', 'open']
    if request.user.is_superuser or request.user.groups.filter(name='junta').exists():
        valid_division_states = valid_division_states + ['hidden', 'preview']

    try:
        league = League.objects.get(
            Q(year=year),
            Q(season__name=season) | Q(season__slug=season),
            Q(night=division) | Q(night_slug=division),
            state__in=valid_division_states,
        )
    except League.DoesNotExist:
        raise Http404('Division Not Found')

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
    valid_division_states = ['cancelled', 'closed', 'open']
    if request.user.is_superuser or request.user.groups.filter(name='junta').exists():
        valid_division_states = valid_division_states + ['hidden', 'preview']

    try:
        league = League.objects.get(
            Q(year=year),
            Q(season__name=season) | Q(season__slug=season),
            Q(night=division) | Q(night_slug=division),
            state__in=valid_division_states,
        )
    except League.DoesNotExist:
        raise Http404('Division Not Found')

    try:
        registration, created = Registrations.objects.get_or_create(user=request.user, league=league)
    except IntegrityError:
        registration = Registrations.objects.get(user=request.user, league=league)

    if not league.is_open(request.user):
        return render_to_response('leagues/registration/error.html',
            {
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
                if not registration.is_complete and not registration.is_refunded:
                    try:
                        coupon_code = request.POST.get('coupon_code')
                        coupon = Coupon.objects.get(code=coupon_code)
                    except ObjectDoesNotExist:
                        coupon = None

                    if coupon:
                        if coupon.is_valid(league, request.user):
                            registration.coupon = coupon
                            registration.save()

                            messages.success(request, 'Your coupon code has been added and will be redeemed when your registration is completed.')
                        else:
                            success = False
                            messages.error(request, 'The coupon code entered is not valid. The code could be expired or past its use limit.')
                    else:
                        success = False
                        messages.error(request, 'The coupon code entered does not exist.')
                else:
                    success = False
                    messages.error(request, 'Your registration is already complete or refunded.')
            else:
                success = False
                messages.error(request, 'Coupon codes are not accepted for this division.')

        if 'remove_coupon' in request.POST:
            if registration.coupon:
                registration.coupon = None
                registration.save()

                messages.success(request, 'Your coupon has been removed and will not be used with this registration.')
            else:
                success = False
                messages.error(request, 'Could not remove coupon; no coupon is associated with this registration.')

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
            base_url = request.build_absolute_uri(getattr(settings, 'FORCE_SCRIPT_NAME', '/')).replace(request.path_info.replace(' ', '%20'), '')

            paypal_dict = {
                'amount': registration.paypal_price,
                'cancel_return': u'{}/leagues/{}/{}/{}/registration/'.format(base_url, league.year, league.season.slug, league.night_slug),
                'invoice': registration.paypal_invoice_id,
                'item_name': u'{} {} {}'.format(league.season_title, league.year, league.night_title),
                'notify_url': u'{}/leagues/registration/payment/{}'.format(base_url, getattr(settings, 'PAYPAL_CALLBACK_SECRET', 'notification/callback/for/a2ultimate/secret/')),
                'return_url': u'{}/leagues/{}/{}/{}/registration-complete/'.format(base_url, league.year, league.season.slug, league.night_slug),
            }

            paypal_form = PayPalPaymentsForm(initial=paypal_dict)
            # https://ppmts.custhelp.com/app/answers/detail/a_id/165

    return render_to_response('leagues/registration/status.html',
        {
            'paypal_form': paypal_form,
            'league': league,
            'registration': registration,
            'section': 'status',
            'tick_percentage': tick_percentage,
            'coupon_is_valid': registration.coupon.is_valid(league, request.user) if registration.coupon else False,
        },
        context_instance=RequestContext(request))


@csrf_exempt
def registrationcomplete(request, year, season, division):
    return redirect('league_registration', year=year, season=season, division=division)
