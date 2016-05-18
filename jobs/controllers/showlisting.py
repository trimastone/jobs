from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

import jobs.lib.jobslib as jobslib

class ShowListing(object):
    def __init__(self, request):
        self.request = request
        self.jobs_lib = jobslib.get_jobs_lib()

    @view_config(route_name='showlisting', renderer='showlisting.mako')
    def showListing(self):
        """Show the details for the given listing. Details may not be to shown if the user is not validated,
        the listing has not been approved, or the ad has been removed.
        """
        listing_id = self.request.matchdict.get('listing_id', None)
        listing_title = self.request.matchdict.get('listing_title', None)
        listing = self.jobs_lib.getListingById(listing_id)

        # Redirect in case the title of the listing has changed.
        if listing_title != listing.safeTitle():
            return HTTPFound(location=self.request.route_path('showlisting',
                                                              listing_id=listing.listing_id,
                                                              listing_title=listing.safeTitle()))

        return dict(listing=listing, company=listing.user.company)
