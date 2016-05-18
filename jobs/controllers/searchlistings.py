from pyramid.view import view_config

import jobs.lib.jobslib

class SearchListings(object):
    def __init__(self, request):
        self.request = request
        self.jobs_lib = jobs.lib.jobslib.get_jobs_lib()

    @view_config(route_name='searchlistings', renderer='searchlistings.mako')
    def searchListings(self):
        """Show a list of all displayable listings."""
        listings = self.jobs_lib.getListingSearch()
        return dict(listings=listings)
