import sys

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from jobs.lib.model import (
    DBSession,
    Base,
    GroupMembership,
    User,
    )
from jobs.lib.security import hashPassword
import transaction

if __name__ == '__main__':
    config_uri = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        user = User(email=email, password_hash=hashPassword(password))
        DBSession.add(user)
        DBSession.flush()
        DBSession.add(GroupMembership(user_id=user.user_id, group_name='admin'))
