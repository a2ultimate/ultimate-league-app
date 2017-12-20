from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone

from ultimate.leagues.models import Game, League
from ultimate.user.models import Player, PlayerRatings
from ultimate.forms import EditPlayerForm, EditPlayerRatingsForm, EditProfileForm, SignupForm


@login_required
def index(request):
    leagues = League.objects.filter(state__in=['closed', 'open', 'preview']).order_by('league_start_date')
    leagues = [l for l in leagues if l.is_visible(request.user)]

    future_games = Game.objects.filter(
        Q(league__in=leagues) &
        Q(date__gte=timezone.now().date()) &
        Q(teams__teammember__user=request.user)
    ).order_by('date')

    future_games = [game for game in future_games if game.get_display_teams().exists()]

    try:
        next_game = future_games.pop(0)
    except IndexError, Game.DoesNotExist:
        next_game = None

    try:
        following_game = future_games.pop(0)
    except IndexError, Game.DoesNotExist:
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


@atomic
def signup(request):
    form = None

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            Player.objects.get_or_create(user=user,
                defaults={'date_of_birth': form.cleaned_data.get('date_of_birth'),
                    'gender': form.cleaned_data.get('gender')})

            messages.success(request, 'Your account was created. You may now log in.')
            return HttpResponseRedirect(reverse('user'))
        else:
            messages.error(request, 'There was an error on the form you submitted.')

    if not form:
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
            instance.updated = timezone.now()
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
