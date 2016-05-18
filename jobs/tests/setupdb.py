from sqlalchemy import create_engine, engine_from_config
from jobs.lib.model import (
                         DBSession,
                         Base,
                         )

def initTestingDB():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession
# meta.metadata.drop_all(meta.engine)


# def initFuncTestingDB(settings):
#     engine = engine_from_config(settings, 'sqlalchemy.')
#     DBSession.configure(bind=engine)
#     Base.metadata.bind = engine

