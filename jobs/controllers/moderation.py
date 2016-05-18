from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

import jobs.lib.jobslib as jobslib

class Moderation(object):

    def __init__(self, request):
        self.request = request
        self.mailer = get_mailer(self.request)
        self.jobs_lib = jobslib.get_jobs_lib()

    @view_config(route_name='mod', renderer='mod_index.mako', permission='admin')
    def index(self):
        """Display the admin index page."""
        return {}

    @view_config(route_name='mod_listing', renderer='mod_listings.mako', permission='admin')
    def listings(self):
        """Show all the pages that need moderating."""
        listing_list = self.jobs_lib.getListingsMod()
        return dict(listing_list=listing_list)

    @view_config(route_name='mod_listing_approve', permission='admin')
    def approveListing(self):
        """Approve the given listing so that it appears on the listings page."""
        listing_id = self.request.params['listing_id']
        self.jobs_lib.approveListingMod(listing_id)
        return HTTPFound(location=self.request.route_path('mod_listing',))

    @view_config(route_name='mod_listing_remove', permission='admin')
    def removeListing(self):
        """Remove the listing so that it does not appear on the listings page or the moderation page."""
        listing_id = self.request.params['listing_id']
        self.jobs_lib.removeListingMod(listing_id)
        return HTTPFound(location=self.request.route_path('mod_listing',))

    @view_config(route_name='mod_application', renderer='mod_applications.mako', permission='admin')
    def application(self):
        """Display applications that need moderating."""
        application_list = self.jobs_lib.getApplicationsMod()
        return dict(application_list=application_list)

    @view_config(route_name='mod_application_approve', permission='admin')
    def approveApplication(self):
        """Approve the given application. The application gets sent to the user that posted the listing."""
        application_id = self.request.params['application_id']
        application, listing = self.jobs_lib.approveApplicationMod(application_id)
        # Need to set the reply-to header so that the user that posted the listing will be able
        # to contact the user that sent the application.
        extra_headers = {'reply-to': application.email}
        body = """The following is an application for the position of %s that you advertised. Reply to this email if you want to message the applicant directly.

Cover Letter:        
%s\n
Resume:
%s""" % (listing.title, application.cover_letter, application.resume)
        message = Message(subject="Application: %s" % listing.title,
                  sender=self.request.registry.settings['jobs.adminsend'],
                  recipients=[listing.user.email],
                  extra_headers=extra_headers,
                  body=body)
        self.mailer.send_to_queue(message)
        return HTTPFound(location=self.request.route_path('mod_application',))

    @view_config(route_name='mod_application_remove', permission='admin')
    def removeApplication(self):
        """Remove the application from the moderation page without sending it."""
        application_id = self.request.params['application_id']
        self.jobs_lib.removeApplicationMod(application_id)
        return HTTPFound(location=self.request.route_path('mod_application',))
