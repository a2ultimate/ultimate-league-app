from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from ultimate.forms import RegistrationAttendanceForm
from ultimate.leagues.models import *
from ultimate.middleware.http import Http403

from paypal.standard.forms import PayPalPaymentsForm


def index(request, year=None, season=None):
	if year and season:
		leagues = League.objects.filter(year=year, season=season).order_by('league_start_date')
	elif year:
		leagues = League.objects.filter(year=year).order_by('-league_start_date')
	else:
		leagues = League.objects.all().order_by('-league_start_date')

	if not request.user.is_superuser and not request.user.groups.filter(name='junta').exists():
		leagues = leagues.filter(state__in=['closed', 'open'])
	elif not request.user.is_superuser:
		leagues = leagues.filter(state__in=['closed', 'open', 'preview'])

	return render_to_response('leagues/index.html',
		{
			'leagues': leagues,
			'year': year,
			'season': season
		},
		context_instance=RequestContext(request))


def summary(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)
	return render_to_response('leagues/summary.html',
		{
			'league': league
		},
		context_instance=RequestContext(request))


def details(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)
	return render_to_response('leagues/details.html',
		{
			'league': league
		},
		context_instance=RequestContext(request))


def players(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)

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
			'unassigned_registrations': unassigned_registrations
		},
		context_instance=RequestContext(request))


def teams(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)
	games = league.get_games()
	sorted_games = sorted(games, key=lambda game: game.date)
	next_game_date = None
	today = date.today()

	for game in sorted_games:
		if game.date >= today and game.date <= today + timedelta(days=7):
			next_game_date = game.date
			break

	if request.user.is_authenticated():
		user_games = league.get_user_games(request.user)
	else:
		user_games = None

	return render_to_response('leagues/teams.html',
	{
		'league': league,
		'field_names': league.get_field_names(),
		'games': games,
		'next_game_date': next_game_date,
		'teams': Team.objects.filter(league=league, hidden=False),
		'user_games': user_games
	},
	context_instance=RequestContext(request))


@login_required
def group(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)
	registration = get_object_or_404(Registrations, league=league, user=request.user)

	if request.method == 'POST':
		if 'leave_group' in request.POST:
			message = registration.leave_baggage_group()
			if message == True:
				messages.success(request, 'You were successfully removed from your baggage group.')
			elif isinstance(message, str):
				messages.error(request, message)
			else:
				messages.error(request, 'You could not be removed from your baggage group.')


		elif 'add_group' in request.POST and 'email' in request.POST:
			email = request.POST.get('email')
			message = registration.add_to_baggage_group(email)
			if (message == True):
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


@login_required
def registration(request, year, season, division, section=None):
	league = get_object_or_404(League, year=year, season=season, night=division)

	if not league.is_open(request.user):
		raise Http403

	try:
		registration, created = Registrations.objects.get_or_create(user=request.user, league=league)
	except IntegrityError:
		registration = Registrations.objects.get(user=request.user, league=league)

	try:
		if ((not registration.is_complete) and
			(not request.user.get_profile()) or
			(not request.user.get_profile().is_complete_for_user) or
			(not request.user.playerratings_set.filter(submitted_by=request.user, user=request.user))):

			raise Http403
	except ObjectDoesNotExist:
		raise Http403

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
		if 'id' in request.POST and 'attendance' in request.POST and 'captain' in request.POST:
			attendance_form = RegistrationAttendanceForm(request.POST, instance=registration)
			if attendance_form.is_valid():
				attendance_form.save()

				if not registration.baggage_id:
					baggage = Baggage()
					baggage.save()
					registration.baggage_id = baggage.id
					registration.save()

				if league.check_price == 0 or league.paypal_price == 0:
					registration.registered = datetime.now()
					registration.save()

				messages.success(request, 'Attendance and captaining response saved.')

			else:
				success = False
				section = 'attendance'
				messages.error(request, 'You must provide a valid attendance and captaining rating to continue.')

		# payment type response
		if 'pay_type' in request.POST:
			if request.POST.get('pay_type').lower() == 'check':
				registration.pay_type = 'check'
				registration.save()
				messages.success(request, 'Payment type set to check.')

			elif request.POST.get('pay_type').lower() == 'paypal':
				registration.pay_type = 'paypal'
				registration.save()
				messages.success(request, 'Payment type set to PayPal.')

			else:
				success = False
				section = 'pay_type'
				messages.error(request, 'You must select a valid payment type to continue.')

		if success:
			return HttpResponseRedirect(reverse('league_registration', kwargs={'year': year, 'season': season, 'division': division}))

	if section == 'conduct' or not registration.conduct_complete:
		return render_to_response('leagues/registration/conduct.html',
			{
				'league': league,
				'registration': registration,
				'section': 'conduct'
			},
			context_instance=RequestContext(request))

	if section == 'waiver' or not registration.waiver_complete:
		return render_to_response('leagues/registration/waiver.html',
			{
				'league': league,
				'registration': registration,
				'section': 'waiver'
			},
			context_instance=RequestContext(request))

	if section == 'attendance' or registration.attendance == None or registration.captain == None:
		if not attendance_form:
			attendance_form = RegistrationAttendanceForm(instance=registration)

		return render_to_response('leagues/registration/attendance.html',
			{
				'league': league,
				'registration': registration,
				'attendance_form': attendance_form,
				'section': 'attendance'
			},
			context_instance=RequestContext(request))

	if league.check_price > 0 or league.paypal_price > 0:

		if section == 'pay_type' or not registration.pay_type or (registration.pay_type != 'check' and registration.pay_type != 'paypal'):
			return render_to_response('leagues/registration/payment.html',
				{
					'league': league,
					'registration': registration,
					'section': 'pay_type'
				},
				context_instance=RequestContext(request))

		if not registration.paypal_invoice_id:
			registration.paypal_invoice_id = str(uuid.uuid4())
			registration.save()

		if not registration.paypal_complete and not registration.check_complete:
			baseUrl = request.build_absolute_uri(getattr(settings, 'FORCE_SCRIPT_NAME', '/')).replace(request.path_info.replace(' ', '%20'), '')

			paypal_dict = {
				'amount': league.paypal_price,
				'cancel_return': baseUrl + '/leagues/' + str(league.year) + '/' + str(league.season) + '/' + str(league.night) + '/registration/',
				'invoice': registration.paypal_invoice_id,
				'item_name': str(league.season).capitalize() + ' League ' + str(league.year) + ' - ' + str(league.night).capitalize(),
				'notify_url': baseUrl + '/leagues/registration/payment/notification/callback/for/a2ultimate/secret/',
				'return_url': baseUrl + '/leagues/' + str(league.year) + '/' + str(league.season) + '/' + str(league.night) + '/registration-complete/',
			}

			paypal_form = PayPalPaymentsForm(initial=paypal_dict)
			# https://ppmts.custhelp.com/app/answers/detail/a_id/165

	return render_to_response('leagues/registration/status.html',
		{
			'paypal_form': paypal_form,
			'league': league,
			'registration': registration,
			'section': 'status'
		},
		context_instance=RequestContext(request))


@csrf_exempt
def registrationcomplete(request, year, season, division):
	return redirect('league_registration', year=year, season=season, division=division)

