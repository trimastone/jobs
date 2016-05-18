import time
import unittest

from pyramid import testing
from pyramid_mailer import get_mailer

import jobs.lib.jobslib as jobslib

class TestMisc(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        self.theapp = app
        from webtest import TestApp
        self.testapp = TestApp(app)
        registry = self.testapp.app.registry
        self.mailer = get_mailer(registry)
        self.jobs_lib = jobslib.get_jobs_lib()

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def testContactForm(self):
        sendEmail = 'm@trimastone.com'
        feedbackMessage = "This is my feedback."
        res = self.testapp.get('/contact/')
        form = res.form
        form['email'] = sendEmail
        form['message'] = feedbackMessage
        res = form.submit()

        assert "Feedback Sent" in res
        assert len(self.mailer.queue) == 1
        message = self.mailer.queue[0]
        print message.recipients
        assert message.recipients == ['admin@trimastone.com']
        assert feedbackMessage in message.body
