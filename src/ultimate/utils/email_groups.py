from ultimate.utils.google_api import GoogleAppsApi


def add_to_group(group_id=None, group_email_address=None, email_address=None, file_path=None):
    api = GoogleAppsApi()
    success_count = 0

    if email_address:
        if api.add_group_member(email_address, group_id=group_id, group_email_address=group_email_address):
            success_count = success_count + 1

    elif file_path:
        try:
            f = open(file_path, 'r')
            email_list = f.read().splitlines()

            for email_address in email_list:
                if api.add_group_member(email_address, group_id=group_id, group_email_address=group_email_address):
                    success_count = success_count + 1

        finally:
            if f is not None:
                f.close()

    return success_count


def generate_email_list_address(league, team=None, suffix=None):
    if league.type == 'league':
        group_address = '{}{}-{}-{}'.format(
            league.season.slug,
            str(league.year)[-2:],
            league.league_start_date.strftime('%a'),
            league.level,
        )
    else:
        group_address = '{}{}-{}'.format(
            league.season.slug,
            str(league.year)[-2:],
            league.night_slug,
        )

    if team is not None:
        group_address += '-' + str(team.id)

    if suffix is not None:
        group_address += '-' + suffix

    return (group_address + '@lists.annarborultimate.org').lower()


def generate_email_list_name(league, team=None, suffix=None):
    if league.type == 'league':
        group_name = '{} {} {} {}'.format(
            league.season.name,
            league.year,
            league.league_start_date.strftime('%A'),
            league.display_level,
        )
    else:
        group_name = '{} {} {}'.format(
            league.season.name,
            league.year,
            league.night,
        )

    if team is not None:
        group_name += ' Team ' + str(team.id)

    if suffix is not None:
        group_name += ' ' + suffix

    return group_name
