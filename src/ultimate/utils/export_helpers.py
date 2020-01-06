def get_export_headers(export_type):
    headers_placement = [
        'Team',
        'Captain',
    ]

    headers_info = [
        'Firstname',
        'Lastname',
        'Email',
        'Gender',
        'Age',
    ]

    headers_payment = [
        'Registration Status',
        'Registration Timestamp',
        'Registration Waitlisted',
        'Registration Refunded',
        'Payment Type',
        'PayPal Email',
        'PayPal Amount',
        'Attendance',
        'Captaining',
    ]

    if export_type == 'league':
        headers_group = [
            'Group',
            'Group Size',
        ]

        headers_ratings = [
            'Rating Total',
            'Experience',
            'Strategy',
            'Throwing',
            'Athleticism',
            'Competitiveness',
            'Spirit',
            'Number of Teams',
        ]

        headers_additional_info = [
            'Height Inches',
            'Guardian Name',
            'Guardian Phone',
            'Prompt Response',
        ]

        return headers_placement + headers_group + headers_info + headers_ratings + headers_additional_info + headers_payment

    if export_type == 'year':
        headers_league = [
            'Division',
        ]

        return headers_league + headers_placement + headers_info + headers_payment

    return headers_placement + headers_info + headers_payment


def get_export_values(export_type, registration_data):
    values_placement = [
        registration_data['team_id'],
        registration_data['is_captain'],
    ]

    values_info = [
        registration_data['first_name'],
        registration_data['last_name'],
        registration_data['email'],
        registration_data['gender'],
        registration_data['age'],
    ]

    values_payment = [
        registration_data['registration_status'],
        registration_data['registration_timestamp'],
        registration_data['registration_waitlisted'],
        registration_data['registration_refunded'],
        registration_data['payment_type'],
        registration_data['paypal_email'],
        registration_data['paypal_amount'],
        registration_data['attendance'],
        registration_data['captaining'],
    ]

    if export_type == 'league':
        values_group = [
            registration_data['baggage_id'],
            registration_data['baggage_size'],
        ]

        values_ratings = [
            registration_data['rating_total'],
            registration_data['rating_experience'],
            registration_data['rating_strategy'],
            registration_data['rating_throwing'],
            registration_data['rating_athleticism'],
            registration_data['rating_competitiveness'],
            registration_data['rating_spirit'],
            registration_data['num_teams'],
        ]

        values_additional_info = [
            registration_data['height'],
            registration_data['guardian_name'],
            registration_data['guardian_phone'],
            registration_data['prompt_response'],
        ]

        return values_placement + values_group + values_info + values_ratings + values_additional_info + values_payment

    if export_type == 'year':
        values_league = [
            registration_data['league'],
        ]

        return values_league + values_placement + values_info + values_payment
