from datetime import date, datetime

from django import forms
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from a2ultimate.leagues.models import *
from a2ultimate.user.models import *
from a2ultimate.forms import *

@login_required
def index(request):
	current_leagues = League.objects.filter(state='active').order_by('-league_start_date')

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
	for league in current_leagues:
		for registration in league.get_league_registrations_for_user(request.user):
			registrations.append(registration)

	return render_to_response('user/index.html',
		{'next_game': next_game, 'following_game': following_game, 'current_leagues': current_leagues, 'registrations': registrations},
		context_instance=RequestContext(request))

def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			new_user = form.save()
			return HttpResponseRedirect(reverse('user'))
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
		player = None

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
def editskills(request):
#	try:
#		skills = Skills.objects.get(user=request.user, submitted_by=request.user)
#	except Skills.DoesNotExist:
#		skills = None

	skills, created = Skills.objects.get_or_create(user=request.user, submitted_by=request.user,
		defaults={'user':request.user, 'updated': datetime.now()})

	if request.method == 'POST':
		form = EditSkillsForm(request.POST, instance=skills)
		if form.is_valid():
			form.save()
			messages.success(request, 'Your skills were updated successfully.')
			return HttpResponseRedirect(reverse('editskills'))
		else:
			messages.error(request, 'There was an error on the form you submitted.')
	else:
		form = EditSkillsForm(instance=skills)

	return render_to_response('user/editskills.html',
		{'form': form},
		context_instance=RequestContext(request))