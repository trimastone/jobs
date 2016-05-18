import urllib

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.session import check_csrf_token

import jobs.lib.jobslib as jobslib

import deform
from deform import Form
import colander

# Various form schemas for the forms used in the add listing process.
class ListingSchema(colander.MappingSchema):
    csrf_token = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget())
    company = colander.SchemaNode(colander.String(), validator=colander.Length(max=200))
    location = colander.SchemaNode(colander.String(), validator=colander.Length(max=200))
    title = colander.SchemaNode(colander.String(), title='Job Title', validator=colander.Length(max=200))
    description = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(rows=15),
                                      validator=colander.Length(max=20000))

class Schema(colander.MappingSchema):
    listing = ListingSchema(title='Enter Listing Information')
schema = Schema()

class ListingLoginSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), validator=colander.Email())

class LoginSchema(colander.MappingSchema):
    login = ListingLoginSchema(title='Contact Information')
login_schema = LoginSchema()

removeChoies = (('filled_here', 'The job has been filled with an applicant from this site.'),
                ('filled_other', 'The job has been filled with an applicant from another source.'),
                ('not_offering', "We're no longer offering this position."),
                ('internal_hire', 'We went with someone already in the organization.'),
                ('other', 'Other'),)
class RemoveSchema(colander.Schema):
    removal_reason = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in removeChoies]),
        widget=deform.widget.RadioChoiceWidget(values=removeChoies),
        title='Why are you removing the ad?',
        description='',)
    csrf_token = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget())
removeSchema = RemoveSchema()

class AddListing(object):
    def __init__(self, request):
        self.request = request
        self.mailer = get_mailer(self.request)
        self.jobs_lib = jobslib.get_jobs_lib()

    def getListingForm(self, user):
        """Create the listing form schema object for the given user."""
        listing = colander.SchemaNode(colander.Mapping(), name="listing")

        if user.company_id:
            listing.add(colander.SchemaNode(colander.String(), title="Company", name="company", missing=user.company.name, widget=deform.widget.TextInputWidget(readonly=True)))
        else:
            listing.add(colander.SchemaNode(colander.String(), name="company", validator=colander.Length(max=200)))

        listing.add(colander.SchemaNode(colander.String(), name="csrf_token", widget=deform.widget.HiddenWidget()))
        listing.add(colander.SchemaNode(colander.String(), name="location", validator=colander.Length(max=200)))
        listing.add(colander.SchemaNode(colander.String(), name="title", title='Job Title', validator=colander.Length(max=200)))
        listing.add(colander.SchemaNode(colander.String(), name="description", widget=deform.widget.TextAreaWidget(rows=15), validator=colander.Length(max=20000)))

        schema = colander.SchemaNode(colander.Mapping())
        schema.add(listing)
        return schema

    def sendValidationEmail(self, user):
        """Send an email to the given user that contains the url they need to visit to validate their email."""
        path = self.request.route_path('emailval', user_id=user.user_id) + "?val_token=%s" % user.val_token
        print path
        link = "http://%s%s" % (self.request.registry.settings['jobs.domain'], path)
        # send val email
        message = Message(subject="Validation Email",
                          sender=self.request.registry.settings['jobs.adminsend'],
                          recipients=[user.email],
                          body="Open this link in your web browser to validate your email address: %s" % link)
        self.mailer.send_to_queue(message)

    @view_config(route_name='addlisting_login', renderer='addlisting_login.mako')
    def addListingLogin(self):
        """Deal with the first page of the add listing process - getting the user's email address.
        When a new user submits their email, a new account is created for them, they get sent the validation email,
        and they get logged in to their new account. They are then sent to the add company page.
        """
        if self.request.authenticated_userid:
            return HTTPFound(location=self.request.route_path('addlisting'))

        myform = Form(login_schema, buttons=('submit',))

        if self.request.method == 'POST':
            controls = self.request.POST.items()  # get the form controls

            try:
                appstruct = myform.validate(controls)  # call validate
            except deform.ValidationFailure as e:  # catch the exception
                return {'form':e.render()}  # re-render the form with an exception

            user_email = appstruct['login']['email'].lower()
            try:
                user = self.jobs_lib.getUserByEmail(user_email)
            except jobslib.JobsUserNotFoundException:
                user = None

            if not user:
                user = self.jobs_lib.createUser(user_email)
                self.jobs_lib.flushChanges()
                self.sendValidationEmail(user)
                headers = remember(self.request, user.user_id)
                return HTTPFound(location=self.request.route_path('addcompany'), headers=headers)
            else:
                qs = urllib.urlencode(dict(came_from=self.request.route_path('addlisting'), email=user_email))
                location = self.request.route_path('login') + "?" + qs
                return HTTPFound(location=location)
        else:
            return dict(form=myform.render())

    @view_config(route_name='addlisting', renderer='addlisting.mako', permission='loggedin')
    @view_config(route_name='editlisting', renderer='addlisting.mako', permission='loggedin')
    def addListing(self):
        """Deal with the third page of the add listing process. The user submits the details of the listing,
        and these are saved to a new listing object. The user is then sent to the add listing page for the
        new listing.
        """
        listing_id = self.request.matchdict.get('listing_id', None)

        if listing_id:
            listing = self.jobs_lib.getListingById(listing_id)
            if listing.user_id != self.request.authenticated_userid:
                return HTTPForbidden()
        else:
            listing = self.jobs_lib.newListing()

        user = self.jobs_lib.getUserById(self.request.authenticated_userid)

        myform = Form(self.getListingForm(user), buttons=('Post Add',))

        if self.request.method == 'POST':
            check_csrf_token(self.request)

            controls = self.request.POST.items()  # get the form controls

            try:
                appstruct = myform.validate(controls)  # call validate
            except deform.ValidationFailure as e:  # catch the exception
                return {'form':e.render()}  # re-render the form with an exception

            self.jobs_lib.createUpdateListing(user, listing, **appstruct['listing'])

            if listing.user.email_validated is False:
                self.sendValidationEmail(listing.user)

            return HTTPFound(location=self.request.route_path('showlisting',
                                                              listing_id=listing.listing_id,
                                                              listing_title=listing.safeTitle()))
        else:
            appstruct = dict(listing=dict(csrf_token=self.request.session.get_csrf_token()))
            if user.company_id:
                appstruct['listing']['company'] = user.company.name

            if listing_id:
                # Display the edit form with pre-existing values
                columns = self.jobs_lib.getColumns(listing)
                for key in columns:
                    appstruct['listing'][key] = getattr(listing, key)

            return dict(form=myform.render(appstruct))


    @view_config(route_name='removelisting', renderer='generic_form.mako', permission='loggedin')
    def removeListing(self):
        """Deal with the listing removal page. The user is asked to give the reason they are removing
        the listing, then it is removed.
        """
        listing_id = self.request.matchdict.get('listing_id', None)

        if listing_id:
            listing = self.jobs_lib.getListingById(listing_id)
            if listing.user_id != self.request.authenticated_userid:
                return HTTPForbidden()

        myform = Form(removeSchema, buttons=('Remove Listing',))

        if self.request.method == 'POST':
            check_csrf_token(self.request)
            controls = self.request.POST.items()  # get the form controls

            try:
                appstruct = myform.validate(controls)  # call validate
            except deform.ValidationFailure as e:  # catch the exception
                return {'form':e.render()}  # re-render the form with an exception

            user = self.jobs_lib.getUserById(self.request.authenticated_userid)
            if not listing.removal_reason:
                self.jobs_lib.removeListing(user, listing, appstruct['removal_reason'])

            self.request.override_renderer = 'generic_message.mako'

            return dict(heading="Listing Removed",
                        messageList=["Your listing will no longer appear on the site.",
                                     "Thank you for using %s." % self.request.registry.settings['jobs.sitename']])
        else:
            appstruct = dict(csrf_token=self.request.session.get_csrf_token())
            return dict(form=myform.render(appstruct))
