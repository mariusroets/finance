import re
import pandas as pd
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from .dbmanager import Base
import hashlib

### Many-to-many relationships
regex_tag = Table('regex_tag', Base.metadata,
        Column('tag_id', ForeignKey('tag.id'), primary_key=True),
        Column('regex_id', ForeignKey('regex.id'), primary_key=True))
transaction_tag = Table('transaction_tag', Base.metadata,
        Column('transaction_id', ForeignKey('transaction.id'), primary_key=True),
        Column('tag_id', ForeignKey('tag.id'), primary_key=True))
taggroup_tag = Table('taggroup_tag', Base.metadata,
        Column('taggroup_id', ForeignKey('tag_group.id'), primary_key=True),
        Column('tag_id', ForeignKey('tag.id'), primary_key=True))

class Tag(Base):
    """Defines the tags that a transaction can be tagged with"""
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)
    description = Column(String(100))

    transactions = relationship('Transaction', secondary=transaction_tag, back_populates='tags')
    regexs = relationship('Regex', secondary=regex_tag, back_populates='tags')
    groups = relationship('TagGroup', secondary=taggroup_tag, back_populates='tags')

    def __repr__(self):
        """String representation
        """
        return "{}-{}".format(self.id, self.name)

class Regex(Base):
    """Defines a list of regular expression to search for in descriptions"""
    __tablename__ = "regex"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    tags = relationship('Tag', secondary=regex_tag, back_populates='regexs')
    
    def __repr__(self):
        """String representation
        """
        return "{}-{}".format(self.id, self.name)

class Account(Base):
    """Defines the accounts"""
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)

    transactions = relationship("Transaction", back_populates="account")

    def __repr__(self):
        """String representation
        """
        return "{}-{}".format(self.id, self.name)

class Transaction(Base):
    """Defines a transaction"""
    __tablename__ = 'transaction'

    # SHA256 of the following string:
    # date(yyyy-mm-dd)#description#amount(.2f)#account_name
    id = Column(Integer, primary_key=True)
    key = Column(String(66), unique=True)
    date = Column(Date)
    effective_month = Column(Date)
    amount = Column(Float)
    description = Column(String(1000))
    balance = Column(Float)
    account_id = Column(Integer, ForeignKey('account.id'))

    account = relationship("Account", back_populates="transactions")
    tags = relationship('Tag', secondary=transaction_tag, back_populates='transactions')

    def createHash(self):
        """Creates a hash from record values to create a unique key
        :returns: None
        """
        self.key = hashlib.sha256(
                bytearray(
                    "{}#{}#{}#{}#{}".format(
                        self.date.isoformat(), 
                        self.description, 
                        self.amount, 
                        self.account.name,
                        self.balance), 
                    'utf-8')).hexdigest()

        
    def __repr__(self):
        """String representation
        """
        return "{}: {}({})".format(self.id, self.description, self.amount)

class TagGroup(Base):
    """Defines the tag groups"""
    __tablename__ = 'tag_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)

    tags = relationship("Tag", secondary=taggroup_tag, back_populates="groups")

    def __repr__(self):
        """String representation
        """
        return "{}-{}".format(self.id, self.name)

def createDefaultData():
    """Creates the default data for the database
    :returns: TODO

    """
    session.add_all([
        Account(name = 'Cheque'),
        Account(name = 'Credit Card'),
        Account(name = 'Private One'),
        Account(name = 'Home Loan BM'),
        Account(name = 'Home Loan KV'),
        Account(name = 'Savings')])

#############################################
### End of data model
#############################################

if __name__ == "__main__":
    import datetime as dt
    tm = TransactionManager()
    t = tm.transactions(dt.date(2021,4,1), with_tags=True)
    t2 = tm.untagged(dt.date(2021,4,1))
    
