import os
import subprocess

from setuptools import setup, find_packages

git_hash = subprocess.check_output("git rev-parse HEAD", shell=True).strip()
print git_hash

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    'webtest',
    'sqlalchemy',
    'pyramid_tm',
    'zope.sqlalchemy',
    'mako',
    'pyramid_mako',
    'deform',
    'pyramid_mailer',
    'psycopg2',
    'PasteScript',
    'nose',
    'coverage',
    ]

test_requires = [
    'webtest',
    ]

setup(name='jobs',
      version=git_hash,
      description='jobs',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      test_suite="jobs",
      entry_points="""\
      [paste.app_factory]
      main = jobs:main
      [console_scripts]
      initialize_tutorial_db = blog.initialize_db:main
      """,
      )
