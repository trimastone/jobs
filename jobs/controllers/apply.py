from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

import jobs.lib.jobslib as jobslib

import deform
import colander

class ApplicationSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    resume = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(rows=15),
                                 validator=colander.Length(max=20000))
    cover_letter = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(rows=15),
                                       validator=colander.Length(max=20000))

class Schema(colander.MappingSchema):
    application = ApplicationSchema()

schema = Schema()

from deform import Form

class Apply(object):
    def __init__(self, request):
        self.request = request
        self.jobs_lib = jobslib.get_jobs_lib()

    @view_config(route_name='apply', renderer='apply.mako')
    def apply(self):
        """Deal with the user applying to a job."""
        listing_id = self.request.matchdict.get('listing_id', None)
        if listing_id:
            listing = self.jobs_lib.getListingById(listing_id)

        myform = Form(schema, buttons=('submit',))
        if self.request.method == 'POST':
            controls = self.request.POST.items()  # get the form controls

            try:
                appstruct = myform.validate(controls)  # call validate
            except deform.ValidationFailure as e:  # catch the exception
                return {'form':e.render()}  # re-render the form with an exception

            self.jobs_lib.createApplication(listing, **appstruct['application'])
            return HTTPFound(location=self.request.route_path('apply_success'))
        else:
            return dict(form=myform.render())

    @view_config(route_name='apply_success', renderer='apply_success.mako')
    def applySucces(self):
        """Return the application success page."""
        return dict()
