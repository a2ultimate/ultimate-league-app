from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from ultimate.leagues.models import *

from ultimate.forms import RegistrationAttendanceForm
from ultimate.middleware.http import Http403

from paypal.standard.forms import PayPalPaymentsForm

def index(request, year, season):
	if request.user.is_superuser:
		leagues = League.objects.filter(year=year, season=season).order_by('league_start_date')
	elif request.user.is_staff:
		leagues = League.objects.filter(year=year, season=season, state__in=['active', 'planning']).order_by('league_start_date')
	else:
		leagues = League.objects.filter(year=year, season=season, state__in=['active']).order_by('league_start_date')

	return render_to_response('leagues/index.html',
		{'leagues': leagues, 'year': year, 'season': season},
		context_instance=RequestContext(request))

def summary(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)
	return render_to_response('leagues/summary.html',
		{'league': league},
		context_instance=RequestContext(request))

def details(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)
	return render_to_response('leagues/details.html',
		{'league': league},
		context_instance=RequestContext(request))

def players(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)

	registrations = league.get_completed_registrations()
	waitlist = league.get_waitlisted_registrations()

	return render_to_response('leagues/players.html',
		{'league': league, 'registrations': registrations, 'waitlist': waitlist},
		context_instance=RequestContext(request))

def teams(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)

	return render_to_response('leagues/teams.html',
		{'league': league, 'field_names': league.get_field_names(), 'teams': Team.objects.filter(league=league), 'user_games': league.get_user_games(request.user)},
		context_instance=RequestContext(request))

@login_required
def group(request, year, season, division):
	league = get_object_or_404(League, year=year, season=season, night=division)
	registration = get_object_or_404(Registrations, league=league, user=request.user)

	if request.method == 'POST':
		if 'leave_group' in request.POST:
			if (registration.leave_baggage_group()):
				messages.success(request, 'You were successfully removed from your baggage group.')
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
		{'league': league, 'registration': registration},
		context_instance=RequestContext(request))

@login_required
def registration(request, year, season, division, section=None):
	league = get_object_or_404(League, year=year, season=season, night=division)

	if league.state not in ['active'] and not request.user.is_staff and not request.user.is_superuser:
		raise Http403

	registration, created = Registrations.objects.get_or_create(user=request.user, league=league)
	attendance_form = None
	paypal_form = None

	if request.method == 'POST':
		# conduct response
		if 'conduct_accept' in request.POST:
			registration.conduct_complete = 1
			registration.save()
			messages.success(request, 'Code of conduct response saved.')
		elif 'conduct_decline' in request.POST:
			registration.conduct_complete = 0
			registration.save()
			messages.error(request, 'You must accept the code of conduct to continue.')

		# waiver response
		if 'waiver_accept' in request.POST:
			registration.waiver_complete = 1
			registration.save()
			messages.success(request, 'Waiver response saved.')
		elif 'waiver_decline' in request.POST:
			registration.waiver_complete = 0
			registration.save()
			messages.error(request, 'You must accept the waiver to continue.')

		# attendance/captaining response
		if 'id' in request.POST and 'attendance' in request.POST and 'captain' in request.POST:
			attendance_form = RegistrationAttendanceForm(request.POST, instance=registration)
			if attendance_form.is_valid():
				attendance_form.save()
				messages.success(request, 'Attendance and captaining response saved.')
			else:
				messages.error(request, 'You must provide an attendance and captaining rating to continue.')

		# payment type response
		if 'pay_type' in request.POST:
			if request.POST.get('pay_type').lower() == 'check':
				if not registration.baggage_id:
					baggage = Baggage()
					baggage.save()
					registration.baggage_id = baggage.id

				registration.pay_type = 'check'
				registration.save()
				messages.success(request, 'Payment type set to check.')

			elif request.POST.get('pay_type').lower() == 'paypal':
				if not registration.baggage_id:
					baggage = Baggage()
					baggage.save()
					registration.baggage_id = baggage.id

				registration.pay_type = 'paypal'
				registration.save()
				messages.success(request, 'Payment type set to PayPal.')

			else:
				messages.error(request, 'You must select a valid payment type to continue.')

		return HttpResponseRedirect(reverse('league_registration', kwargs={'year': year, 'season': season, 'division': division}))

	if section == 'conduct' or not registration.conduct_complete:
		return render_to_response('leagues/registration/conduct.html',
			{'league': league, 'registration': registration},
			context_instance=RequestContext(request))

	if section == 'waiver' or not registration.waiver_complete:
		return render_to_response('leagues/registration/waiver.html',
			{'league': league, 'registration': registration},
			context_instance=RequestContext(request))

	if section == 'attendance' or registration.attendance == None or registration.captain == None:
		attendance_form = RegistrationAttendanceForm(instance=registration)
		return render_to_response('leagues/registration/attendance.html',
			{'attendance_form': attendance_form, 'league': league, 'registration': registration},
			context_instance=RequestContext(request))

	if section == 'pay_type' or not registration.pay_type or (registration.pay_type != 'check' and registration.pay_type != 'paypal'):
		return render_to_response('leagues/registration/payment.html',
			{'league': league, 'registration': registration},
			context_instance=RequestContext(request))

	if not registration.paypal_invoice_id:
		registration.paypal_invoice_id = str(uuid.uuid4())
		registration.save()

	if not registration.paypal_complete and not registration.check_complete:
		baseUrl = request.build_absolute_uri(getattr(settings, 'FORCE_SCRIPT_NAME', ''))

		paypal_dict = {
			'amount': league.paypal_cost,
			'cancel_return': baseUrl + '/leagues/' + str(league.year) + '/' + str(league.season) + '/' + str(league.night) + '/registration/',
			'invoice': registration.paypal_invoice_id,
			'item_name': str(league.season).capitalize() + ' League ' + str(league.year) + ' - ' + str(league.night).capitalize(),
			'notify_url': baseUrl + '/leagues/registration/payment/notification/callback/for/a2ultimate/secret/',
			'return_url': baseUrl + '/leagues/' + str(league.year) + '/' + str(league.season) + '/' + str(league.night) + '/registration/',
		}

		paypal_form = PayPalPaymentsForm(initial=paypal_dict)
		# https://ppmts.custhelp.com/app/answers/detail/a_id/165

	return render_to_response('leagues/registration/status.html',
		{'paypal_form': paypal_form, 'league': league, 'registration': registration, 'section': section},
		context_instance=RequestContext(request))





