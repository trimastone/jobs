import unittest

from pyramid import testing
import transaction

import jobs.lib.jobslib as jobslib
import setupacc

class TestSearch(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        self.theapp = app
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.jobs_lib = jobslib.get_jobs_lib()

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def addUser(self, email, password, company_name, **kw):
        company_id = setupacc.createCompany(company_name)
        user_id = setupacc.createUser(email, password, company_id=company_id, **kw)

    def testSearchPage(self):
        title1 = "Testing Software Dev 1"
        title2 = "Testing Software Dev 2"
        title3 = "Testing Software Dev 3"
        title4 = "Testing Software Dev 4"
        company_name1 = "test company 11"
        company_name2 = "test company 22"
        self.addUser("m@trimastone.com", '123', company_name1, email_validated=True)
        self.addUser("m2@trimastone.com", '123', company_name2)
        user1 = self.jobs_lib.getUserById(1)
        user2 = self.jobs_lib.getUserById(2)
        with transaction.manager:
            self.jobs_lib.createListing(user1, title=title1, approved=True, removal_reason=None)
            self.jobs_lib.createListing(user1, title=title2, approved=False, removal_reason=None)
            self.jobs_lib.createListing(user1, title=title3, approved=True, removal_reason='filled_here')
            self.jobs_lib.createListing(user2, title=title4, approved=True, removal_reason=None)

        res = self.testapp.get('/s/')
        print res
        assert title1 in res
        assert title2 not in res
        assert title3 not in res
        assert title4 not in res
