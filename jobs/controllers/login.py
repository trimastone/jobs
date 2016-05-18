from pyramid.view import view_config
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )

import jobs.lib.jobslib

class Login(object):
    def __init__(self, request):
        self.request = request
        self.jobs_lib = jobs.lib.jobslib.get_jobs_lib()

    @view_config(request_method='GET', route_name='login', renderer='login.mako')
    def loginForm(self):
        """Display the login form."""
        came_from = self.request.params.get('came_from', '')
        email = self.request.params.get('email', '')
        return dict(came_from=came_from, email=email)

    @view_config(request_method='POST', route_name='login', renderer='login.mako')
    def loginSubmit(self):
        """Checks that the user has submitted the correct login information. If they have, the authentication
        cookies get set and the user is sent to the page they were attempting to access that resulted in
        the login form being displayed in the first place.
        """
        came_from = self.request.params.get('came_from', '/')
        if not came_from:
            came_from = '/'
        print came_from
        username = self.request.params['username'].strip()
        password = self.request.params['password'].strip()
        user, password_val = self.jobs_lib.isCorrectPassword(username, password)
        if password_val:
            headers = remember(self.request, user.user_id)
            return HTTPFound(location=came_from, headers=headers)
        else:
            return dict(came_from=came_from, email=username)

    @view_config(request_method='GET', route_name='logout', permission='loggedin')
    def logOut(self):
        """Logs the user out by removing the authentication cookies."""
        headers = forget(self.request)
        return HTTPFound(location=self.request.route_path('home'), headers=headers)
