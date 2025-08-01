import time
from ultimate.utils.google_api import GoogleAppsApi


def add_to_group(
    group_id=None, group_email_address=None, email_address=None, file_path=None
):
    api = GoogleAppsApi()
    success_count = 0

    if email_address:
        time.sleep(2)
        if api.add_group_member(
            email_address,
            group_id=group_id,
            group_email_address=group_email_address,
        ):
            success_count = success_count + 1

    elif file_path:
        try:
            opened_file = open(file_path, "r")
            email_list = opened_file.read().splitlines()

            for email_address in email_list:
                if api.add_group_member(
                    email_address,
                    group_id=group_id,
                    group_email_address=group_email_address,
                ):
                    success_count = success_count + 1

        finally:
            if opened_file is not None:
                opened_file.close()

    return success_count


def generate_email_list_address(league, team=None, suffix=None):
    if league.type == "league":
        descriptor = league.level
        if not league.gender == "corec":
            descriptor = "{}-{}".format(league.level, league.gender)

        group_address = "{}{}-{}-{}".format(
            league.season.slug,
            str(league.year)[-2:],
            league.league_start_date.strftime("%a"),
            descriptor,
        )
    else:
        group_address = "{}{}-{}".format(
            league.season.slug,
            str(league.year)[-2:],
            league.night_slug,
        )

    if team is not None:
        group_address += "-" + str(team.id)

    if suffix is not None:
        group_address += "-" + suffix

    return "{}@lists.annarborultimate.org".format(group_address).lower()


def generate_email_list_name(league, team=None, suffix=None):
    if league.type == "league":
        descriptor = league.display_level
        if not league.gender == "corec":
            descriptor = "{} {}".format(
                league.display_level,
                league.display_gender,
            )

        group_name = "{} {} {} {}".format(
            league.season.name,
            league.year,
            league.league_start_date.strftime("%A"),
            descriptor,
        )
    else:
        group_name = "{} {} {}".format(
            league.season.name,
            league.year,
            league.night,
        )

    if team is not None:
        group_name += " - Team " + str(team.id)

    if suffix is not None:
        group_name += " - " + suffix

    return group_name
