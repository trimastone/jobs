import time
import unittest

from pyramid import testing

import jobs.lib.jobslib as jobslib
import setupacc

class TestLogin(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        self.theapp = app
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.jobs_lib = jobslib.get_jobs_lib()

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def testNormalLogin(self):
        email = "m@m.com"
        password = '123'
        res = setupacc.createAndLogin(self.testapp, email, password)
        assert res.status_int == 302
        print self.testapp.cookies.keys()
        assert len(self.testapp.cookies['auth_tkt']) > 0

        res = self.testapp.get('/logout/', status=302)
        print self.testapp.cookies.keys()
        assert 'auth_tkt' not in self.testapp.cookies

    def testBadLogin(self):
        email = "m@m.com"
        password = '123'
        setupacc.createUser(email, password)
        res = self.testapp.get('/login/')
        form = res.form
        form['username'] = email
        form['password'] = 'wrongpassword'
        form.submit()
        assert res.status_int == 200
        print self.testapp.cookies.keys()
        assert 'auth_tkt' not in self.testapp.cookies
