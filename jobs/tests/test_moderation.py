import unittest

from pyramid import testing
from pyramid_mailer import get_mailer
import transaction

import jobs.lib.jobslib as jobslib
import setupacc

title = "listing title"
description = "Some description"
resume = "test resume"
cl = "test cover letter"
email = "m@trimastone.com"
password = '123'

class TestModeration(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        self.theapp = app
        from webtest import TestApp
        self.testapp = TestApp(app)
        registry = self.testapp.app.registry
        self.mailer = get_mailer(registry)
        self.jobs_lib = jobslib.get_jobs_lib()

        setupacc.createAdminAndLogin(self.testapp, 'admin@trimastone.com', '123')

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def addListing(self):
        company_id = setupacc.createCompany('test company')
        user_id = setupacc.createUser('m@trimastone.com', '123', company_id=company_id)
        with transaction.manager:
            user = self.jobs_lib.getUserById(user_id)
            self.jobs_lib.createListing(user, title=title, description=description)

    def addApplication(self):
        with transaction.manager:
            user_id = setupacc.createUser(email, password)
            user = self.jobs_lib.getUserById(user_id)
            listing = self.jobs_lib.createListing(user, title=title, description=description, user_id=user_id)
            self.jobs_lib.createApplication(listing, resume=resume, cover_letter=cl)

    def testListingApprove(self):
        self.addListing()
        res = self.testapp.get('/mod/listing/')
        res = res.click(linkid="approve_1")
        listing = self.jobs_lib.getListingById(1)
        assert listing.approved is True

    def testListingRemove(self):
        self.addListing()
        res = self.testapp.get('/mod/listing/')
        res = res.click(linkid="remove_1")
        listing = self.jobs_lib.getListingById(1)
        assert listing.approved is False

    def testApplicationApprove(self):
        self.addApplication()
        res = self.testapp.get('/mod/application/')
        print res
        res = res.click(linkid="approve_1")
        application = self.jobs_lib.getApplicationById(1)
        assert application.approved is True

        assert len(self.mailer.queue) == 1
        message = self.mailer.queue[0]
        assert message.sender == 'admin@trimastone.com'
        assert message.subject == 'Application: %s' % title
        assert message.recipients == [email]
        assert resume in message.body
        assert cl in message.body

    def testApplicationRemove(self):
        self.addApplication()

        res = self.testapp.get('/mod/application/')
        res = res.click(linkid="remove_1")
        application = self.jobs_lib.getApplicationById(1)
        assert application.approved is False
        assert len(self.mailer.queue) == 0

    def testNotMod(self):
        setupacc.createAndLogin(self.testapp, 'notadmin@trimastone.com', '123')
        res = self.testapp.get('/mod/listing/', status=403)
