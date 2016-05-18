import unittest

from pyramid import testing
import transaction

import jobs.lib.jobslib as jobslib
import setupacc

title = "TestingSoftwareDev"
company_name = "test company"
description = "job desc"
location = "Vancouver"
email = "test@trimastone.com"
password = "123"

class TestShow(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        self.theapp = app
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.jobs_lib = jobslib.get_jobs_lib()

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def addUser(self, **kw):
        company_id = setupacc.createCompany(company_name)
        user_id = setupacc.createUser(email, password, company_id=company_id, **kw)
        return user_id

    def testShowNonLoggedIn(self):
        user_id = self.addUser(email_validated=True)
        with transaction.manager:
            user = self.jobs_lib.getUserById(user_id)
            self.jobs_lib.createListing(user, title=title, description=description, location=location, approved=True)

        res = self.testapp.get('/l/1/%s/' % title, status=200)
        assert title in res
        assert company_name in res

        res = self.testapp.get('/l/1/wrongtitle/', status=302)
        print res.location
        assert title in res.location

    def testShowLoggedIn(self):
        """
        User can still view their listings when logged in even if the listing would
        not show for other users, logged in or not.
        """
        user_id = self.addUser()
        setupacc.login(self.testapp, email, password)
        with transaction.manager:
            user = self.jobs_lib.getUserById(user_id)
            self.jobs_lib.createListing(user, title=title, description=description, location=location, approved=False,
                                        removal_reason="here")
        res = self.testapp.get('/l/1/%s/' % title, status=200)
        assert title in res
        assert company_name in res

    def testNoShowRemoved(self):
        user_id = self.addUser(email_validated=True)
        with transaction.manager:
            user = self.jobs_lib.getUserById(user_id)
            self.jobs_lib.createListing(user, title=title, description=description, location=location, approved=True,
                                        removal_reason="here")

        res = self.testapp.get('/l/1/%s/' % title, status=200)
        assert title not in res
        assert company_name not in res
        assert "no longer available" in res

    def testNoShowEmailNotValid(self):
        user_id = self.addUser()
        with transaction.manager:
            user = self.jobs_lib.getUserById(user_id)
            self.jobs_lib.createListing(user, title=title, description=description, location=location, approved=True)

        res = self.testapp.get('/l/1/%s/' % title, status=200)
        assert title not in res
        assert company_name not in res
        assert "Listing Pending" in res

    def testNoShowNotApproved(self):
        user_id = self.addUser(email_validated=True)
        with transaction.manager:
            user = self.jobs_lib.getUserById(user_id)
            self.jobs_lib.createListing(user, title=title, description=description, location=location, approved=False)

        res = self.testapp.get('/l/1/%s/' % title, status=200)
        assert title not in res
        assert company_name not in res
        assert "removed" in res

