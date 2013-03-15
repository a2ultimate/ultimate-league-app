def menu_leagues(request):
	from ultimate.leagues.models import League
	return {'menu_leagues': League.objects.filter(state='active').order_by('league_start_date')}