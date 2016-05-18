import unittest

from pyramid import testing
import transaction

import jobs.lib.jobslib as jobslib
import setupacc

title = "listing title"
description = "Some description"
company_name = 'test company'

class TestApply(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        self.theapp = app
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.jobs_lib = jobslib.get_jobs_lib()

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def addListing(self):
        company_id = setupacc.createCompany(company_name)
        user_id = setupacc.createUser('m@trimastone.com', '123', company_id=company_id)
        with transaction.manager:
            user = self.jobs_lib.getUserById(user_id)
            self.jobs_lib.createListing(user, title=title, description=description)

    def testApply(self):
        email = 'app@trimastone.com'
        resume = 'test resume'
        cover_letter = 'test cover letter'
        self.addListing()

        res = self.testapp.get('/p/1/')
        form = res.form
        form['resume'] = resume
        form['cover_letter'] = cover_letter
        form['email'] = email
        res = form.submit()
        applications = self.jobs_lib.getAllApplications()
        assert applications[0].resume == resume
        assert applications[0].cover_letter == cover_letter
        assert applications[0].email == email

        assert res.status_int == 302
        res = res.follow()
        assert 'success' in res
