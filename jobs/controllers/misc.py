import os

from pyramid.httpexceptions import HTTPFound
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.response import Response
from pyramid.view import view_config

import deform
from deform import Form
import colander

class ContactSchemaBase(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    message = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(rows=15),
                                  validator=colander.Length(max=20000))

class ContactSchema(colander.MappingSchema):
    contact = ContactSchemaBase(title='Contact Form')

schema = ContactSchema()

class Misc(object):
    def __init__(self, request):
        self.request = request
        self.mailer = get_mailer(self.request)

    @view_config(route_name='contact', renderer='generic_form.mako')
    def contactUs(self):
        """Deal the the contact form."""
        myform = Form(schema, buttons=('submit',))
        if self.request.method == 'POST':
            controls = self.request.POST.items()  # get the form controls

            try:
                appstruct = myform.validate(controls)  # call validate
            except deform.ValidationFailure as e:  # catch the exception
                return {'form':e.render()}  # re-render the form with an exception

            email = appstruct['contact']['email']
            userMessage = appstruct['contact']['message']

            modEmail = self.request.registry.settings['jobs.adminsend']
            extra_headers = {'reply-to': email}
            message = Message(subject="Feedback",
                          sender=modEmail,
                          recipients=[modEmail],
                          extra_headers=extra_headers,
                          body=userMessage)
            self.mailer.send_to_queue(message)

            self.request.override_renderer = 'generic_message.mako'
            return dict(heading="Feedback Sent",
                        messageList=["Thank you for using %s." % self.request.registry.settings['jobs.sitename']])
        else:
            return dict(form=myform.render())

    @view_config(route_name='robots.txt')
    def robotsTxt(self):
        if self.request.registry.settings['jobs.demo'] == 'true':
            robotsFile = 'robots.txt_demo'
        else:
            robotsFile = 'robots.txt'
        here = os.path.dirname(__file__)
        robots = open(os.path.join(here, '../static', robotsFile)).read()
        return Response(content_type='text/plain', body=robots)
