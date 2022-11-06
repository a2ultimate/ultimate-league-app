header_strings = [
    'Division', # 0
    'Team', # 1
    'Captain', # 2
    'Firstname', # 3
    'Lastname', # 4
    'Email', # 5
    'Match Pref', # 6
    'Age', # 7
    'Registration Status', # 8
    'Registration Timestamp', # 9
    'PayPal Email', # 10
    'Attendance', # 11
    'Captaining', # 12
    'Registration Waitlisted', # 13
    'Registration Refunded', # 14
    'Payment Type', # 15
    'PayPal Amount', # 16
    'Group', # 17
    'Group Size', # 18
    'Rating Total', # 19
    'Experience', # 20
    'Strategy', # 21
    'Throwing', # 22
    'Athleticism', # 23
    'Competitiveness', # 24
    'Spirit', # 25
    'Number of Teams', # 26
    'Height Inches', # 27
    'Guardian Name', # 28
    'Guardian Email', # 29
    'Guardian Phone', # 30
    'Prompt Response', # 31
]

value_keys = [
    'league', # 0
    'team_id', # 1
    'is_captain', # 2
    'first_name', # 3
    'last_name', # 4
    'email', # 5
    'gender', # 6
    'age', # 7
    'registration_status', # 8
    'registration_timestamp', # 9
    'paypal_email', # 10
    'attendance', # 11
    'captaining', # 12
    'registration_waitlisted', # 13
    'registration_refunded', # 14
    'payment_type', # 15
    'paypal_amount', # 16
    'baggage_id', # 17
    'baggage_size', # 18
    'rating_total', # 19
    'rating_experience', # 20
    'rating_strategy', # 21
    'rating_throwing', # 22
    'rating_athleticism', # 23
    'rating_competitiveness', # 24
    'rating_spirit', # 25
    'num_teams', # 26
    'height', # 27
    'guardian_name', # 28
    'guardian_email', # 29
    'guardian_phone', # 30
    'prompt_response', # 31
]

admin_export_columns = [1, 2, 17, 18, 3, 4, 5, 6, 7, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 8, 9, 13, 14, 15, 10, 16, 11, 12]
captain_export_columns = [17, 18, 3, 4, 5, 6, 7, 19, 20, 24, 25, 26, 30, 10, 11, 12]
year_export_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 15, 10, 16, 11, 12]

def get_admin_export_headers():
    return list(map(lambda i: header_strings[i], admin_export_columns))

def get_captain_export_headers():
    return list(map(lambda i: header_strings[i], captain_export_columns))

def get_year_export_headers():
    return list(map(lambda i: header_strings[i], year_export_columns))

def get_admin_export_values(data):
    return list(map(lambda i: data[value_keys[i]], admin_export_columns))

def get_captain_export_values(data):
    return list(map(lambda i: data[value_keys[i]], captain_export_columns))

def get_year_export_values(data):
    return list(map(lambda i: data[value_keys[i]], year_export_columns))

def get_export_headers(export_type, report_format):
    if export_type == 'league':
        if report_format == 'admin':
            return get_admin_export_headers()
        if report_format == 'captain':
            return get_captain_export_headers()
    if export_type == 'year':
        return get_year_export_headers()


def get_export_values(export_type, report_format, registration_data):
    if export_type == 'league':
        if report_format == 'admin':
            return get_admin_export_values(registration_data)
        if report_format == 'captain':
            return get_captain_export_values(registration_data)
    if export_type == 'year':
        return get_year_export_values(registration_data)
