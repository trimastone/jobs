from pyramid.view import view_config

class Home(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='home.mako')
    def home(self):
        """Render the home page."""
        return dict()
