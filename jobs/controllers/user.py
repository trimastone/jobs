import urllib

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.view import view_config
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from pyramid.session import check_csrf_token

import colander
import deform

import jobs.lib.jobslib as jobslib

class PasswordChangeReqBase(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
class PasswordChangeReqSchema(colander.MappingSchema):
    req = PasswordChangeReqBase(title="Enter your email:")
req_schema = PasswordChangeReqSchema()

class PasswordChangeBase(colander.MappingSchema):
    csrf_token = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget())
    password = colander.SchemaNode(colander.String(), validator=colander.Length(max=50))
    val_token = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget())

class PasswordChangeSchema(colander.MappingSchema):
    req = PasswordChangeBase(title='Enter your new password:')
change_schema = PasswordChangeSchema()

class UserMod(object):

    def __init__(self, request):
        self.request = request
        self.mailer = get_mailer(self.request)
        self.jobs_lib = jobslib.get_jobs_lib()

    @view_config(route_name='changepw_req', renderer='generic_form.mako')
    def changePasswordReq(self):
        """Deal with a password change request. The user is asked to give the email for the account. If the email
        is associated with an account, the password reset link is emailed to the user.
        """
        myform = deform.Form(req_schema, buttons=('submit',))
        if self.request.method == 'POST':
            controls = self.request.POST.items()  # get the form controls

            try:
                appstruct = myform.validate(controls)  # call validate
            except deform.ValidationFailure as e:  # catch the exception
                return {'form':e.render()}  # re-render the form with an exception

            email = appstruct['req']['email']
            user = self.jobs_lib.getUserByEmail(email)
            path = self.request.route_path('changepw', user_id=user.user_id) + "?" + urllib.urlencode(dict(val_token=user.val_token))

            link = "http://%s%s" % (self.request.registry.settings['jobs.domain'], path)
            print link
            # send change email
            message = Message(subject="Password Reset",
                              sender=self.request.registry.settings['jobs.adminsend'],
                              recipients=[user.email],
                              body="Open this link in your web browser to change your password: %s" % link)
            self.mailer.send_to_queue(message)

            self.request.override_renderer = 'generic_message.mako'

            return dict(heading="Password Change Email Sent",
                        messageList=["You should receive an email that will allow you to reset your password.",
                                     "Please follow the instructions within that email."])

        else:
            return dict(form=myform.render())

    @view_config(route_name='changepw', renderer='generic_form.mako')
    def changePassword(self):
        """Deal with password changes. To access the form, the correct val_token must be given as one of the
        parameters to ensure that only users with access to the email account associated with the account
        will be able to change the password.
        """
        user_id = self.request.matchdict['user_id']
        val_token = self.request.params.get('val_token', '')
        myform = deform.Form(change_schema, buttons=('submit',))
        appstruct = dict(req=dict(val_token=val_token, csrf_token=self.request.session.get_csrf_token()))
        if self.request.method == 'POST':
            check_csrf_token(self.request)
            controls = self.request.POST.items()  # get the form controls

            try:
                appstruct = myform.validate(controls)  # call validate
            except deform.ValidationFailure as e:  # catch the exception
                return {'form':e.render()}  # re-render the form with an exception

            password = appstruct['req']['password']
            val_token = appstruct['req']['val_token']
            try:
                self.jobs_lib.changePassword(user_id, password, val_token)
                self.request.override_renderer = 'generic_message.mako'
                return dict(heading="Your Password Has Been Changed",
                            messageList=["Click the Login link above to log in."])
            except jobslib.JobsPasswordChangeTokenWrongException:
                return HTTPNotFound()
        else:
            return dict(form=myform.render(appstruct))
