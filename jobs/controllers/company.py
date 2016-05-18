import colander
import deform
from deform import Form
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.view import view_config
import sqlalchemy.inspection

import jobs.lib.jobslib as jobslib

class CompanySchema(colander.MappingSchema):
    csrf_token = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget())
    name = colander.SchemaNode(colander.String(), validator=colander.Length(max=100), title="Company Name")
    size = colander.SchemaNode(colander.String(), validator=colander.Length(max=100), missing=None)
    market = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(rows=15),
                                 validator=colander.Length(max=20000), missing=None,
                                 title="Describe your company's market")
    culture = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(rows=15),
                                  validator=colander.Length(max=20000), missing=None,
                                  title="Describe your company's culture.")
    software_meth = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(rows=15),
                                        validator=colander.Length(max=20000), missing=None,
                                        title="Describe your company's software development methodology")

class CompanySchemaMap(colander.MappingSchema):
    company = CompanySchema()
companySchema = CompanySchemaMap()

class CompanyController(object):
    def __init__(self, request):
        self.request = request
        self.jobs_lib = jobslib.get_jobs_lib()

    @view_config(route_name='addcompany', renderer='generic_form.mako', permission='loggedin')
    @view_config(route_name='editcompany', renderer='generic_form.mako', permission='loggedin')
    def addCompany(self):
        """Deal with add company page. Once the user submits company info, it is saved to the
        database.
        """
        company_id = self.request.matchdict.get('company_id', None)
        user = self.jobs_lib.getUserById(self.request.authenticated_userid)

        if company_id:
            company = self.jobs_lib.getCompanyById(company_id)
            if company.company_id != user.company_id:
                return HTTPForbidden()

        myform = Form(companySchema, buttons=('submit',))
        if self.request.method == 'POST':
            controls = self.request.POST.items()  # get the form controls

            try:
                appstruct = myform.validate(controls)  # call validate
            except deform.ValidationFailure as e:  # catch the exception
                return {'form':e.render()}  # re-render the form with an exception
            if not company_id:
                company = self.jobs_lib.newCompany()

            self.jobs_lib.createUpdateCompany(user, company, **appstruct['company'])

            # Send the user to different pages depending on whether they are editing the company info
            # or they are in the add listing work flow.
            if company_id:
                return HTTPFound(location=self.request.route_path('showcompany', company_id=company_id))
            else:
                return HTTPFound(location=self.request.route_path('addlisting'))
        else:
            appstruct = dict(company=dict(csrf_token=self.request.session.get_csrf_token()))

            if company_id:
                # Display the edit form with pre-existing values
                for key in self.jobs_lib.getColumns(company):
                    if getattr(company, key) is not None:
                        appstruct['company'][key] = getattr(company, key)
                    else:
                        appstruct['company'][key] = ""

            return dict(form=myform.render(appstruct), sub_header="Let potential employees know what your company is all about")

    @view_config(route_name='showcompany', renderer='showcompany.mako')
    def showCompany(self):
        """Display information about the given company."""
        company_id = self.request.matchdict.get('company_id', None)
        company = self.jobs_lib.getCompanyById(company_id)
        user = None
        if self.request.authenticated_userid:
            user = self.jobs_lib.getUserById(self.request.authenticated_userid)
        return dict(company=company, user=user)
