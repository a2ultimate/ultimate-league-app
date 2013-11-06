def menu_leagues(request):
	from ultimate.leagues.models import League

	leagues = League.objects.filter(state__in=['closed', 'open', 'preview']).order_by('league_start_date')
	leagues = [r for r in leagues if r.is_visible(request.user)]

	return {'menu_leagues': leagues}