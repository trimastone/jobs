import json
import os.path

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import SignedCookieSessionFactory

from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    )

from sqlalchemy import create_engine

import lib.jobslib
from lib.model import DBSession, Base
from lib.security import groupfinder

class RootFactory(object):
    """The authorizing config for the application.
    """
    __acl__ = [(Allow, Authenticated, 'loggedin'),
               (Allow, 'admin', 'admin'),
               ]
    def __init__(self, request):
        pass

def get_engine(secrets):
    """Create a sqlalchemy engine object with settings from a json file.
    Args:
        secrets: json data from secrets file.
    Returns:
        The newly created sqlalchemy engine object.
    """
    path = "postgresql://%(db_user)s:%(db_password)s@%(db_ip)s/%(db_name)s" % secrets
    return create_engine(path)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Configure database access
    secrets_path = settings['secrets_path']
    if not os.path.isabs(secrets_path):
        secrets_path = os.path.join(os.path.dirname(__file__), '../', secrets_path)
    secrets = json.load(open(secrets_path, 'r'))
    engine = get_engine(secrets)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    # Recreate the database if this is a test run.
    if settings.get('jobs.test', None) == 'true':
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    lib.jobslib.init_jobs_lib(secrets['password_string'])
    authn_policy = AuthTktAuthenticationPolicy(secrets['auth_secret'], hashalg='sha512', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    # Add password string to the settings dictionary so it can be accessed elsewhere.
    settings['jobs.password_string'] = secrets['password_string']
    config = Configurator(settings=settings, root_factory='jobs.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    my_session_factory = SignedCookieSessionFactory(secrets['cookie_secret'])
    config.set_session_factory(my_session_factory)
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')
    config.add_route('home', '/')
    config.add_route('addlisting_login', '/a/')
    config.add_route('addlisting', '/a/listing/')
    config.add_route('editlisting', '/a/{listing_id}/')
    config.add_route('removelisting', '/remove_listing/{listing_id}/')
    config.add_route('showlisting', '/l/{listing_id}/{listing_title}/')
    config.add_route('searchlistings', '/s/')
    config.add_route('addcompany', '/ac/')
    config.add_route('editcompany', '/ac/{company_id}/')
    config.add_route('showcompany', '/showcompany/{company_id}/')
    config.add_route('apply_success', '/p/success/')
    config.add_route('apply', '/p/{listing_id}/')
    config.add_route('emailval', '/emailval/{user_id}/')
    config.add_route('login', '/login/')
    config.add_route('logout', '/logout/')
    config.add_route('changepw_req', '/cpw_req/')
    config.add_route('changepw', '/cpw/{user_id}/')
    config.add_route('mod_application', '/mod/application/')
    config.add_route('mod_application_approve', '/mod/application/approve/')
    config.add_route('mod_application_remove', '/mod/application/remove/')
    config.add_route('mod_listing', '/mod/listing/')
    config.add_route('mod_listing_approve', '/mod/listing/approve/')
    config.add_route('mod_listing_remove', '/mod/listing/remove/')
    config.add_route('mod', '/mod/')
    config.add_route('contact', '/contact/')
    config.add_route('robots.txt', '/robots.txt')
    config.scan()
    return config.make_wsgi_app()
