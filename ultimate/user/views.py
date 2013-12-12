from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from ultimate.leagues.models import *
from ultimate.user.models import *
from ultimate.forms import *


@login_required
def index(request):
	leagues = League.objects.filter(state__in=['closed', 'open', 'preview']).order_by('league_start_date')
	leagues = [r for r in leagues if r.is_visible(request.user)]

	# date.today() OR something like date(2010, 4, 13)
	next_games = Game.objects.filter(Q(date__gte=date.today()) & Q(Q(gameteams__team__teammember__user=request.user) | Q(gameteams__team__teammember__user=request.user))).order_by('date')[0:2]
	try:
		next_game = next_games[0:1].get()
	except Game.DoesNotExist:
		next_game = None

	try:
		following_game = next_games[1:2].get()
	except Game.DoesNotExist:
		following_game = None

	registrations = []
	for league in leagues:
		for registration in league.get_registrations_for_user(request.user):
			registrations.append(registration)

	return render_to_response('user/index.html',
		{
			'current_leagues': leagues,
			'following_game': following_game,
			'next_game': next_game,
			'registrations': registrations
		},
		context_instance=RequestContext(request))


def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			form.save()

			messages.success(request, 'Your account was created. You may now log in.')
			return HttpResponseRedirect(reverse('user'))
		else:
			messages.error(request, 'There was an error on the form you submitted.')
	else:
		form = SignupForm()
	return render_to_response('user/signup.html',
		{'form': form},
		context_instance=RequestContext(request))


@login_required
def editprofile(request):
	try:
		player = Player.objects.get(user=request.user)
	except Player.DoesNotExist:
		player = Player(user=request.user)

	if request.method == 'POST':
		form = EditProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save(commit=False)
			player_form = EditPlayerForm(request.POST, instance=player)
			if player_form.is_valid():
				form.save()
				player_form.save()
				messages.success(request, 'Your profile was updated successfully.')
				return HttpResponseRedirect(reverse('editprofile'))
			else:
				messages.error(request, 'There was an error on the form you submitted.')
		else:
			player_form = EditPlayerForm(request.POST, instance=player)
			messages.error(request, 'There was an error on the form you submitted.')
	else:
		form = EditProfileForm(instance=request.user)
		player_form = EditPlayerForm(instance=player)
	return render_to_response('user/editprofile.html',
		{'form': form, 'player_form': player_form},
		context_instance=RequestContext(request))


@login_required
def editratings(request):
	try:
		ratings = PlayerRatings.objects.get(user=request.user, submitted_by=request.user, ratings_type=PlayerRatings.RATING_TYPE_USER)
	except PlayerRatings.DoesNotExist:
		ratings = None

	if request.method == 'POST':
		form = EditPlayerRatingsForm(request.POST, instance=ratings)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.ratings_type = PlayerRatings.RATING_TYPE_USER
			instance.submitted_by = request.user
			instance.updated = datetime.now()
			instance.user = request.user
			instance.save()

			messages.success(request, 'Your ratings were updated successfully.')
			return HttpResponseRedirect(reverse('editratings'))
		else:
			messages.error(request, 'There was an error on the form you submitted.')
	else:
		form = EditPlayerRatingsForm(instance=ratings)

	return render_to_response('user/editratings.html',
		{
			'form': form
		},
		context_instance=RequestContext(request)
	)
