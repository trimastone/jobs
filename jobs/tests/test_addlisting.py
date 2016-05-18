import time
import unittest

from pyramid import testing
from pyramid_mailer import get_mailer
from sqlalchemy import inspect
import transaction

import jobs.lib.jobslib as jobslib
import setupacc

company_name = 'test company'
email = "m@m.com"
password = '123'

import transaction

class TestAddListing(unittest.TestCase):
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

    def addUser(self, email, password, **kw):
        company_id = setupacc.createCompany(company_name)
        user_id = setupacc.createUser(email, password, company_id=company_id, **kw)

    def testPost(self):
        """
        Try to add listing with no pre-existing user.
        """
        email = "m@trimastone.com"
        res = self.testapp.get('/a/', status=200)
        form = res.form
        form['email'] = email
        res = form.submit()
        assert res.status_int == 302
        user = self.jobs_lib.getAllUsers()[0]
        assert user.email == email

        assert len(self.mailer.queue) == 1
        message = self.mailer.queue[0]
        assert message.sender == 'admin@trimastone.com'
        assert message.subject == 'Validation Email'
        assert message.recipients == [email]

        form = res.follow().form
        form['name'] = company_name
        form['size'] = '42'
        res = form.submit()
        assert res.status_int == 302
        company = self.jobs_lib.getAllCompanies()[0]
        assert company.name == company_name

        res = res.follow()
        assert company_name in res
        form = res.form
        form['location'] = 'test location'
        form['title'] = 'test company software dev'
        form['description'] = 'job description'
        res = form.submit()
        assert res.status_int == 302
        listing = self.jobs_lib.getAllListings()[0]
        assert listing.approved is None
        assert listing.user_id == user.user_id

    def testEdit(self):
        title = 'test title'
        new_title = 'new test title'
        email = "m@trimastone.com"
        password = '123'
        self.addUser(email, password)
        setupacc.login(self.testapp, email, password)
        with transaction.manager:
            user = self.jobs_lib.getUserById(1)
            self.jobs_lib.createListing(user, title=title)

        res = self.testapp.get('/a/1/', status=200)
        assert title in res

        form = res.form
        form['title'] = new_title
        res = form.submit()
        print res
        listing = self.jobs_lib.getAllListings()[0]
        print (listing.title, new_title)
        assert listing.title == new_title

    def testEditWrongUser(self):
        title = 'test title'
        email = "m@trimastone.com"
        password = '123'
        self.addUser(email, password)
        with transaction.manager:
            user = self.jobs_lib.getUserById(1)
            self.jobs_lib.createListing(user, title=title)
        setupacc.createAndLogin(self.testapp, "another@trimastone.com", '123')
        res = self.testapp.get('/a/1/', status=403)

    def testPostLoggedIn(self):
        email = "m@trimastone.com"
        password = '123'
        self.addUser(email, password)
        setupacc.login(self.testapp, email, password)
        res = self.testapp.get('/a/', status=302)
        assert '/a/listing/' in res.location

        res = res.follow()
        assert company_name in res
        form = res.form
        form['location'] = 'test location'
        form['title'] = 'test company software dev'
        form['description'] = 'job description'
        res = form.submit()

        assert len(self.mailer.queue) == 1
        message = self.mailer.queue[0]
        assert message.sender == 'admin@trimastone.com'
        assert message.subject == 'Validation Email'
        assert message.recipients == [email]

    def testPostNotLoggedIn(self):
        """
        Test that we are sent to the login page when we give a pre-existing user.
        """
        email = "m@m.com"
        password = '123'
        self.addUser(email, password)

        res = self.testapp.get('/a/', status=200)
        form = res.form
        form['email'] = email
        res = form.submit()
        assert res.status_int == 302
        assert '/login/' in res.location

    def testListingNotLoggedIn(self):
        res = self.testapp.get('/a/listing/', status=403)

    def testRemoveListing(self):
        title = 'test title'
        removal_reason = 'filled_here'
        self.addUser(email, password)
        setupacc.login(self.testapp, email, password)
        with transaction.manager:
            user = self.jobs_lib.getUserById(1)
            self.jobs_lib.createListing(user, title=title)

        res = self.testapp.get('/remove_listing/1/')
        form = res.form
        form['deformField1'] = removal_reason
        res = form.submit()
        listing = self.jobs_lib.getAllListings()[0]
        assert listing.removal_reason == removal_reason

    def testRemovalWrongUser(self):
        title = 'test title'
        removal_reason = 'filled_here'
        setupacc.createUser("m@trimastone.com", '123')
        setupacc.createAndLogin(self.testapp, "diff@trimastone.com", "123")
        with transaction.manager:
            user = self.jobs_lib.getUserById(1)
            self.jobs_lib.createListing(user, title=title)
        res = self.testapp.get('/remove_listing/1/', status=403)

    def testPostLoggedInNoCompany(self):
        setupacc.createAndLogin(self.testapp, 'm@trimastone.com', '123')
        res = self.testapp.get('/a/', status=302)
        res = res.follow()
        form = res.form
        form['company'] = company_name
        form['location'] = 'test location'
        form['title'] = 'test company software dev'
        form['description'] = 'job description'
        res = form.submit()
        assert res.status_int == 302
        listings = self.jobs_lib.getAllListings()
        assert len(listings) == 1
        company = self.jobs_lib.getAllCompanies()[0]
        assert company.name == company_name
        user = self.jobs_lib.getAllUsers()[0]
        assert user.company_id == company.company_id
