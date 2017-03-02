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
    group_address = '{}{}-{}-{}'.format(
        league.season.slug,
        league.league_start_date.strftime('%y'),
        league.league_start_date.strftime('%a'),
        league.level,
    )

    if team is not None:
        group_address += '-' + str(team.id)

    if suffix is not None:
        group_address += '-' + suffix

    return (group_address + '@lists.annarborultimate.org').lower()


def generate_email_list_name(league, team=None, suffix=None):
    group_name = '{} {} {} {}'.format(
        league.season.name,
        league.league_start_date.strftime('%Y'),
        league.league_start_date.strftime('%A'),
        league.display_level,
    )

    if team is not None:
        group_name += ' Team ' + str(team.id)

    if suffix is not None:
        group_name += ' ' + suffix

    return group_name
