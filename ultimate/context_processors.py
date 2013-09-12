def menu_leagues(request):
	from ultimate.leagues.models import League

	if request.user.is_superuser or request.user.groups.filter(name='junta').exists():
		leagues = League.objects.filter(state__in=['active', 'planning']).order_by('league_start_date')
	else:
		leagues = League.objects.filter(state__in=['active']).order_by('league_start_date')

	return {'menu_leagues': leagues}