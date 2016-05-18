import unittest

from pyramid import testing
import transaction

from jobs.lib.model import JobsCompanyAlreadyExistsException
import jobs.lib.jobslib as jobslib
import setupacc

class TestCompany(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        self.theapp = app
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.jobs_lib = jobslib.get_jobs_lib()

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def testEdit(self):
        company_name = 'test company'
        new_company_name = 'test company 2'
        size = '42'
        email = 'm@trimastone.com'
        password = '123'
        company_id = setupacc.createCompany(company_name)
        setupacc.createUser(email, password, company_id=company_id)
        setupacc.login(self.testapp, email, password)

        res = self.testapp.get('/ac/1/')
        form = res.form
        form['name'] = new_company_name
        form['size'] = size
        res = form.submit()
        assert res.status_int == 302
        assert 'showcompany' in res.location

        company = self.jobs_lib.getAllCompanies()[0]
        assert company.name == new_company_name
        assert company.size == size

        # Try to use an already existing name, with different capitalization.
        company_id = setupacc.createCompany(company_name)
        res = self.testapp.get('/ac/1/')
        form = res.form
        form['name'] = company_name.upper()
        form['size'] = size
        self.assertRaises(JobsCompanyAlreadyExistsException, form.submit)

    def testEditNotLoggedIn(self):
        company_name = 'test company'
        size = '42'
        email = 'm@trimastone.com'
        password = '123'
        company_id = setupacc.createCompany(company_name)
        setupacc.createUser(email, password, company_id=company_id)
        res = self.testapp.get('/ac/1/', status=403)

    def testEditWrongUser(self):
        company_name = 'test company'
        size = '42'
        email = 'm@trimastone.com'
        password = '123'
        company_id = setupacc.createCompany(company_name)
        setupacc.createUser(email, password, company_id=company_id)
        setupacc.createAndLogin(self.testapp, 'baduser@trimastone.com', '123')
        self.testapp.get('/ac/1/', status=403)
