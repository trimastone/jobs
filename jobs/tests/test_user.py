import time
import unittest

from pyramid import testing
from pyramid_mailer import get_mailer
import transaction

import jobs.lib.jobslib as jobslib
from jobs.lib.security import hashPassword
import setupacc

class TestUser(unittest.TestCase):
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

    def testChangeRequset(self):
        email = "m@trimastone.com"
        password = '123'
        new_password = '12345'
        user_id = setupacc.createUser(email, password)
        user = self.jobs_lib.getUserById(user_id)

        res = self.testapp.get('/cpw_req/')
        form = res.form
        form['email'] = email
        res = form.submit()
        print res
        assert "Password Change Email Sent" in res

        assert len(self.mailer.queue) == 1
        message = self.mailer.queue[0]
        assert message.sender == 'admin@trimastone.com'
        assert message.subject == 'Password Reset'
        assert message.recipients == [email]

        res = self.testapp.get('/cpw/1/?val_token=%s' % user.val_token)
        form = res.form
        form['password'] = new_password
        res = form.submit()
        assert "Your Password Has Been Changed" in res

        user = self.jobs_lib.getUserById(1)
        assert user.password_hash == hashPassword(new_password, self.theapp.registry.settings['jobs.password_string'])

    def testBadChangeRequest(self):
        email = "m@trimastone.com"
        password = '123'
        new_password = '12345'
        setupacc.createUser(email, password)

        res = self.testapp.get('/cpw/1/?val_token=wrongtoken')
        form = res.form
        form['password'] = new_password
        res = form.submit(status=404)
        user = self.jobs_lib.getUserById(1)
        assert user.password_hash == hashPassword(password, self.theapp.registry.settings['jobs.password_string'])
