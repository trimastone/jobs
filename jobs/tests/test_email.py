import unittest

from pyramid import testing
import transaction

import jobs.lib.jobslib as jobslib
import setupacc

email = 'app@trimastone.com'
password = '123'
val_token = '123'

class TestEmail(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        self.theapp = app
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.jobs_lib = jobslib.get_jobs_lib()

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def testEmailVal(self):
        setupacc.createUser(email, password, val_token=val_token)
        res = self.testapp.get('/emailval/1/?val_token=%s' % val_token, status=200)
        user = self.jobs_lib.getAllUsers()[0]
        assert user.email_validated is True

    def testEmailValBadToken(self):
        setupacc.createUser(email, password, val_token=val_token)
        res = self.testapp.get('/emailval/1/badtoken/', status=404)
