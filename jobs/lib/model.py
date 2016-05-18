import random
import string

import markupsafe
from pyramid.security import Allow, Everyone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )
from sqlalchemy.sql import func
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class JobsCompanyAlreadyExistsException(Exception):
    pass

def valTokenGen():
    return ''.join(random.sample(string.ascii_letters, 20))

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    email = Column(Text, unique=True)
    email_validated = Column(Boolean, default=False)
    val_token = Column(Text, default=valTokenGen, nullable=False)
    password_hash = Column(Text)
    company_id = Column(Integer, ForeignKey('companies.company_id'))
    time_created = Column(DateTime, server_default=func.now())

    listings = relationship("Listing", back_populates="user")
    groups = relationship("GroupMembership", back_populates="user")
    company = relationship("Company", back_populates="users")

class Company(Base):
    __tablename__ = 'companies'
    company_id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    size = Column(Text)
    market = Column(Text)
    culture = Column(Text)
    software_meth = Column(Text)
    time_created = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="company")

    def shorten(self, val):
        maxLength = 450
        if len(val) > maxLength:
            val = val[:maxLength] + "..."
        return val

    def shortMarket(self):
        return self.shorten(self.market)

    def shortCulture(self):
        return self.shorten(self.culture)

    def shortSoftwareMeth(self):
        return self.shorten(self.software_meth)

    @classmethod
    def checkName(cls, name):
        name = name.lower()
        companyList = DBSession.query(Company).filter(func.lower(Company.name) == name).all()
        if len(companyList) > 0:
            raise JobsCompanyAlreadyExistsException("That company name is already in use!")

class Listing(Base):
    __tablename__ = 'listings'
    listing_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    title = Column(Text)
    description = Column(Text)
    location = Column(Text)
    approved = Column(Boolean, default=None)
    removal_reason = Column(Text)
    time_removed = Column(DateTime)
    time_created = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="listings")
    applications = relationship("Application", back_populates="listing")

    def htmlSafeDesc(self):
        descLines = [markupsafe.escape(x) for x in self.description.split('\r\n')]
        return '<br />'.join(descLines)

    def safeTitle(self):
        return self.title.replace("/", "-")

class Application(Base):
    __tablename__ = 'applications'
    application_id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey('listings.listing_id'))
    email = Column(Text)
    resume = Column(Text)
    cover_letter = Column(Text)
    approved = Column(Boolean, default=None)
    time_created = Column(DateTime, server_default=func.now())

    listing = relationship("Listing", back_populates="applications")

class GroupMembership(Base):
    __tablename__ = 'group_memberships'
    group_mem_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    group_name = Column(Text)

    user = relationship("User", back_populates="groups")
