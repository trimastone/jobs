import unittest

from pyramid import testing

import jobs.lib.jobslib as jobslib

class TestHome(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini')
        from webtest import TestApp
        self.testapp = TestApp(app)
        self.jobs_lib = jobslib.get_jobs_lib()

    def tearDown(self):
        self.jobs_lib.removeChanges()

    def testHome(self):
        res = self.testapp.get('/')
        assert 'Welcome' in res
