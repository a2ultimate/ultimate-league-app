from ultimate.utils.google_api import GoogleAppsApi


def add_to_group(group_id=None, group_email_address=None,
    email_address=None, file_path=None, team_id=None):

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
