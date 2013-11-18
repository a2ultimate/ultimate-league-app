def menu_leagues(request):
	from ultimate.leagues.models import League

	leagues = League.objects.filter(state__in=['closed', 'open', 'preview']).order_by('league_start_date')
	leagues = [r for r in leagues if r.is_visible(request.user)]

	return {'menu_leagues': leagues}


def user_profile_is_complete(request):
	result = {'user_profile_is_complete': False}
	if request.user and request.user.is_authenticated():
		try:
			result['user_profile_is_complete'] = request.user.get_profile().is_complete_for_user()
		except:
			return result

	return result


def user_rating_is_complete(request):
	result = {'user_rating_is_complete': False}
	if request.user and request.user.is_authenticated():
		try:
			result['user_rating_is_complete'] = bool(not request.user.playerrattings_set.filter(submitted_by=request.user, user=request.user))
		except:
			return result

	return result
