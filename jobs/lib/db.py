from sqlalchemy import and_, func
import sqlalchemy.inspection

from jobs.lib.model import Application, Company, Listing, DBSession, User

def add(obj):
    DBSession.add(obj)

def flushDb():
    DBSession.flush()

def checkCompanyName(company_name):
    return Company.checkName(company_name)

def getCompanyByName(company_name):
    return DBSession.query(Company).filter_by(name=company_name).all()

def getListingSearch():
    listings = DBSession.query(Listing).join(User).filter(and_(Listing.approved == True,
                                                               Listing.removal_reason == None,
                                                               User.email_validated == True)).order_by(Listing.time_created.desc()).all()
    return listings

def getUserByEmail(email):
    return DBSession.query(User).filter_by(email=email).all()

def getUserById(user_id):
    return DBSession.query(User).filter_by(user_id=user_id).all()

def getListingById(listing_id):
    return DBSession.query(Listing).filter_by(listing_id=listing_id).all()

def getColumns(obj):
    insp = sqlalchemy.inspection.inspect(obj)
    return insp.mapper.columns.keys()

def serverNow():
    return func.now()

def remove():
    return DBSession.remove()

def getAllUsers():
    return DBSession.query(User).all()

def getAllCompanies():
    return DBSession.query(Company).all()

def getAllListings():
    return DBSession.query(Listing).all()

def getAllApplications():
    return DBSession.query(Application).all()

def getCompanyById(company_id):
    return DBSession.query(Company).filter_by(company_id=company_id).all()

def getListingsMod():
    return DBSession.query(Listing).filter_by(approved=None).order_by(Listing.time_created.desc())

def getApplicationsMod():
    return DBSession.query(Application).filter_by(approved=None).order_by(Application.time_created.desc())

def getApplicationById(application_id):
    return DBSession.query(Application).filter_by(application_id=application_id).all()
