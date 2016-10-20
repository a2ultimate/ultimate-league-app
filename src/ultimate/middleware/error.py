class ErrorUserMiddleware(object):
    """
    Alter HttpRequest objects on Error
    """
    def process_exception(self, request, exception):
        """
        Add user details.
        """
        try:
            if request.user.is_authenticated():
                request.META['AUTH_USER_NAME'] = str(request.user.first_name) + ' ' + str(request.user.last_name)
                request.META['AUTH_USER_EMAIL'] = str(request.user.email)
                request.META['AUTH_USER_ID'] = str(request.user.id)
                request.META['AUTH_USER_IS_ACTIVE'] = str(request.user.is_active)
                request.META['AUTH_USER_IS_SUPERUSER'] = str(request.user.is_superuser)
                request.META['AUTH_USER_IS_STAFF'] = str(request.user.is_staff)
                request.META['AUTH_USER_LAST_LOGIN'] = str(request.user.last_login)

        except:
            pass
