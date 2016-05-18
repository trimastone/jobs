import db
from model import Application, Company, GroupMembership, Listing, User
import security

class JobsUserNotFoundException(Exception):
    pass

class JobsListingNotFoundException(Exception):
    pass

class JobsCompanyNotFoundException(Exception):
    pass

class JobsApplicationNotFoundException(Exception):
    pass

class JobsEmailValTokenWrongException(Exception):
    pass

class JobsPasswordChangeTokenWrongException(Exception):
    pass

class _JobsLib(object):
    def __init__(self, password_string):
        self.password_string = password_string

    """The main interface to the business logic for the application."""
    def getListingSearch(self):
        """Return list of listings to be displayed on search page."""
        return db.getListingSearch()

    def getUserByEmail(self, email):
        """Return the user object for the given user email address."""
        ret = db.getUserByEmail(email)
        if len(ret) == 0:
            raise JobsUserNotFoundException
        return ret[0]

    def getUserById(self, user_id):
        """Return the user object for the given user_id."""
        ret = db.getUserById(user_id)
        if len(ret) == 0:
            raise JobsUserNotFoundException
        return ret[0]

    def createUser(self, email, **kw):
        """Create a new user object with the given email and add it to the pending database updates.
        The kw values will be passed to the User object's constructor.
        """
        passArgName = 'password'
        if passArgName in kw:
            kw['password_hash'] = security.hashPassword(kw[passArgName], self.password_string)
            kw.pop(passArgName)
        user = User(email=email, **kw)
        db.add(user)
        return user

    def flushChanges(self):
        """Write pending database updates to the database."""
        db.flushDb()

    def removeChanges(self):
        """Remove pending database changes without committing them."""
        return db.remove()

    def getListingById(self, listing_id):
        """Return a listing object for the listing with given listing_id."""
        listings = db.getListingById(listing_id)
        if len(listings) == 0:
            raise JobsListingNotFoundException
        return listings[0]

    def createListing(self, user, **kw):
        """Create a new listing object and add it to the pending database updates. The kw values are passed
        to the Listing object's constructor.
        """
        listing = Listing(**kw)
        self.createUpdateListing(user, listing)
        return listing

    def createUpdateListing(self, user, listing, **kw):
        """Take the given Listing object, set its attributes based on the given kw values,
        then add the object to the pending database changes. If their is a new company listed in the
        kw values, then create the company and set the given user to be associated with the new company. 
        """
        for key, val in kw.iteritems():
            print (key, val)
            setattr(listing, key, val)
        if not listing.user_id:
            listing.user_id = user.user_id

        if user.company_id is None and 'company' in kw:
            company = self.createCompany(kw['company'])
            self.flushChanges()
            user.company_id = company.company_id
            db.add(user)

        db.add(listing)
        self.flushChanges()

    def createCompany(self, company_name, **kw):
        """Create a company with the given company_name"""
        db.checkCompanyName(company_name)
        company = Company(name=company_name, **kw)
        db.add(company)
        return company

    def createUpdateCompany(self, user, company, **kw):
        """Take the given Company object, set its attributes based on the given kw values,
        then add the object to the pending database changes. Associate the company with the
        given user as well.
        """
        if 'name' in kw and company.name != kw['name']:
            Company.checkName(kw['name'])
        for key, val in kw.iteritems():
            print (key, val)
            setattr(company, key, val)
        db.add(company)
        self.flushChanges()
        user.company_id = company.company_id
        db.add(user)

    def newCompany(self):
        """Return a new Company object."""
        return Company()

    def newListing(self):
        """Return a new Listing object."""
        return Listing()

    def removeListing(self, user, listing, removal_reason):
        """Remove the given listing."""
        now = db.serverNow()
        self.createUpdateListing(user, listing, removal_reason=removal_reason, time_removed=now)

    def getColumns(self, obj):
        """Return all the columns from the given database object."""
        return db.getColumns(obj)

    def getAllUsers(self):
        """Return a list of all users in the database."""
        return db.getAllUsers()

    def getAllCompanies(self):
        """Return a list of all companies in the database."""
        return db.getAllCompanies()

    def getAllListings(self):
        """Return a list of all listings in the database."""
        return db.getAllListings()

    def getAllApplications(self):
        """Return a list of all applications in the database."""
        return db.getAllApplications()

    def createApplication(self, listing, **kw):
        """Create a new application object and add it to the pending database changes."""
        application = Application()
        for key, val in kw.iteritems():
            setattr(application, key, val)
        application.listing_id = listing.listing_id
        db.add(application)
        return application

    def getCompanyById(self, company_id):
        """Return company object for company with given company_id."""
        ret = db.getCompanyById(company_id)
        if len(ret) == 0:
            raise JobsCompanyNotFoundException
        return ret[0]

    def getListingsMod(self):
        """Get all listings the need moderation."""
        return db.getListingsMod()

    def approveListingMod(self, listing_id):
        """Approve the listing with id listing_id, and add to pending database changes."""
        listing = self.getListingById(listing_id)
        listing.approved = True
        db.add(listing)

    def removeListingMod(self, listing_id):
        """Remove the listing with id listing_id, and add to pending database changes."""
        listing = self.getListingById(listing_id)
        listing.approved = False
        db.add(listing)

    def getApplicationsMod(self):
        """Get all applications the need moderation."""
        return db.getApplicationsMod()

    def getApplicationById(self, application_id):
        """Returns application object for application with id application_id."""
        ret = db.getApplicationById(application_id)
        if len(ret) == 0:
            raise JobsApplicationNotFoundException
        return ret[0]

    def approveApplicationMod(self, application_id):
        """Approve the application with id application_id, and add to pending database changes."""
        application = self.getApplicationById(application_id)
        application.approved = True
        listing = application.listing
        db.add(application)
        return application, listing

    def removeApplicationMod(self, application_id):
        """Remove the application with id application_id, and add to pending database changes."""
        application = self.getApplicationById(application_id)
        application.approved = False
        db.add(application)

    def addUserGroup(self, user_id, group_name):
        """Add user to the given group and add to pending database changes."""
        db.add(GroupMembership(user_id=user_id, group_name=group_name))

    def validateEmail(self, user_id, val_token):
        user = self.getUserById(user_id)
        if user.val_token == val_token:
            user.email_validated = True
        else:
            raise JobsEmailValTokenWrongException()

    def isCorrectPassword(self, username, password):
        user = self.getUserByEmail(username)
        password_hash = security.hashPassword(password, self.password_string)
        if user.password_hash and password_hash == user.password_hash:
            return user, True
        else:
            return user, False

    def changePassword(self, user_id, password, val_token):
        user = self.getUserById(user_id)
        if user.val_token == val_token:
            # Hash the password
            user.password_hash = security.hashPassword(password, self.password_string)
        else:
            raise JobsPasswordChangeTokenWrongException()

_jobs_lib = None

def get_jobs_lib():
    """Return the _JobsLib singleton for this application."""
    return _jobs_lib

def init_jobs_lib(password_string):
    global _jobs_lib
    _jobs_lib = _JobsLib(password_string)
