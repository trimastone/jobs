from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

import jobs.lib.jobslib as jobslib

class Email(object):

    def __init__(self, request):
        self.request = request
        self.jobs_lib = jobslib.get_jobs_lib()

    @view_config(route_name='emailval', renderer='generic_message.mako')
    def emailVal(self):
        """Called when a user opens the email validation page. Updates the user in the database as validated,
        so that the users's listings can be displayed.
        """
        user_id = self.request.matchdict['user_id']
        val_token = self.request.params['val_token']
        try:
            self.jobs_lib.validateEmail(user_id, val_token)
        except jobslib.JobsEmailValTokenWrongException:
            raise HTTPNotFound()
        return dict(heading="Your Email Has Been Validated.",
                    messageList=["Any listings that you posted will appear after they are approved."])
