import re
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Table
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from finance.utils import Base
import hashlib

#engine = create_engine('sqlite:///data/data.db', echo=True)
engine = create_engine('mysql://finance:finance@192.168.0.105/finance')
Session = sessionmaker(bind=engine)
session = Session()

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


class DBManager:
    """Handles a set of database changes for a specific entity"""

    def __init__(self, session=None):
        """Constructor """
        self.open(session)

    def __del__(self):
        if self._session:
            self._session.close()

    @property
    def session(self):
        """The database session used"""
        return self._session

    def open(self, session=None):
        """Open's a new session"""
        if session:
            self._session = session
        else:
            self._session = Session()

    def close(self):
        """Closes the session"""
        if self._session:
            self._session.close()
            self._session = None
        

class Connection:
    """Connection class forms the basis for queries and updates"""
    def __init__(self):
        """Constructor """
        self._db = None

    @property
    def db(self):
        """The database connection used"""
        return self._db

    def __enter__(self, session=None):
        """Context manager enter function"""
        self._db = DBManager(session)
        return self

    def __exit__(self, *args):
        """Context manager exit function"""
        if self._db:
            self._db.close()
            self._db = None


    def query_pd(self, query):
        """Runs a given query and returns a dataframe"""
        
        with self:
            df = pd.read_sql(query.statement, self.db.session.bind)

        return df


class TransactionManager(Connection):
    """Handles all transaction queries"""

    def exists(self, transaction_id):
        """Returns the transaction if it exists, otherwise False"""
        with self:
            trans = self.db.session.query(Transaction).filter_by(id=transaction_id).one_or_none()

        return trans if trans else False
        
    def untagged(self, month):
        """Returns a list of untagged transactions, for a given month"""
        result = (
            self.transactions(month, with_tags=True)
            .query("tag_name == ' '")
        )

        return result
    
    def tags(self, transaction_id, csv=False):
        """Return the tags associated with a transaction"""
        
    def transactions(self,
                     month,
                     with_tags=False,
                     tags_compressed=True,
                     tag_filter=None,
                     tag_filter_and=False):
        """Return a list of all transactions for a given month

        Args:
            month (date): The first of the month for which transactions should be returned
        Keyword Arguments:
            with_tags (bool): Return tags with transactions
            tags_compressed (bool): If true, return 1 line per transaction, with multiple tags
                formatted as a comma seperated string. If False, one for each tag is returned.
            tag_filter (list(str)): A list of tags to filter on. The list is OR'ed by default
            tag_filter_and (bool): If true, the list in tag_filter is AND'ed. Only if effective
                if len(tag_filter) > 1

        :returns: TODO

        """
        unused_columns = [
            'transaction_key',
            'transaction_effective_month',
            'transaction_balance', 
            'transaction_account_id',
            'account_id',]

        with self:
            if not with_tags:
                query = (
                    self._db.session
                    .query(Transaction, Account)
                    .join(Transaction.account)
                    .with_labels()
                    .filter(Transaction.effective_month == month)
                )
            else:
                query = (
                    self._db.session
                    .query(Transaction, Account, Tag)
                    .join(Transaction.account)
                    .outerjoin(Transaction.tags)
                    .with_labels()
                    .filter(Transaction.effective_month == month)
                )
                unused_columns.append('tag_id')
                unused_columns.append('tag_description')
            result = (
                self.query_pd(query)
                .drop(columns=unused_columns)
                .assign(transaction_date=lambda x: pd.to_datetime(x.transaction_date))
            )
            if tag_filter:
                result = result[result.tag_name.isin(tag_filter)]
                # OR is done if tag_filter_and==False or if there is only one tag
                if tag_filter_and and (len(tag_filter) > 1):
                    temp = (
                        result
                        .groupby('transaction_id')
                        .tag_name
                        .agg([('count', 'count')])
                        .reset_index()
                        .query(f"count == {len(tag_filter)}")
                    )
                    result = result[result.transaction_id.isin(temp.transaction_id)]

            if with_tags and tags_compressed:
                result = (
                    result
                    .assign(tag_name=lambda x: x.tag_name.fillna(' '))
                    .groupby('transaction_id')
                    .agg({
                        'transaction_date': 'first',
                        'transaction_amount': 'first',
                        'transaction_description': 'first',
                        'account_name': 'first',
                        'tag_name': ','.join})
                    .reset_index()
                )


        return result

class TagManager(Connection):
    """Handles all tag queries"""

    def tag_exists(self, tag_name):
        """Checks whether a tag exists in the database

        :tag_name: TODO
        :returns: TODO

        """
        with self:
            tag = self.db.session.query(Tag).filter_by(name=tag_name).one_or_none()

        return tag if tag else False

    def add_tag(self, tag_name, description=""):
        """Adds a new tag to the database

        :tag_name: TODO
        :returns: TODO

        """
        tag = self.tag_exists(tag_name)
        if tag:
            return tag
        with self:
            tag = Tag(name=tag_name, description=description)
            self.db.session.add(tag)
            self.db.session.commit()

        return tag

    def remove_tag(self, tag_name):
        """Removes the given tag from the database. Tags will be remove from all transactions,
        autotags and groups.

        Args:
            tag_name (TODO): TODO

        Returns: TODO

        """
        pass

    def clear_tags(self):
        """Remove all tags that are not used anywhere in the database

        Returns: TODO

        """
        pass


class TransactionTagManager(Connection):
    """Tagging and untagging of transactions"""

    def tag(self, transaction_list, tag_list):
        """Tag the list of transactions with the given list of tags"""
        tagman = TagManager()
        transman = TransactionManager()
        with self:
            for trans in transaction_list:
                transaction = transman.exists(trans)
                if not transaction:
                    print("Transaction does not exist")
                    continue

                for t in tag_list:
                    tag = tagman.add_tag(t)
                    transaction.tags.append(tag)
            
            self.db.session.commit()
        
    def untag(self, transaction_id, tag_name=None):
        """Remove the list of tags from the list of transactions"""
        transman = TransactionManager()
        trans = transman.exists(transaction_id)
        with self:
            if not tag_name:
                trans.tags = []
            else:
                trans.tags = list(filter(lambda t: t.name != tag_name, trans.tags))
            self.db.session.commit()

    def auto_tag(self, month):
        """Auto tag all transactions in a month against all defined regex"""
        regman = RegexManager()
        transman = TransactionManager()
        tagman = TagManager()

        # Make sure all tags exist
        tag_map = regman.regex_list(tags_compressed=False)
        tag_list = tag_map.tag_name.unique()
        for tag in tag_list:
            tagman.add_tag(tag)

        # Compile all regexs
        regexs = tag_map.regex_name.unique()
        regex_comp = {}
        for r in regexs:
            regex_comp[r] = re.compile(r)

        # Get all untagged transactions
        transactions = transman.untagged(month)

        for i, t in transactions.iterrows():
            for tmap in tag_map.to_dict(orient='records'):
                if regex_comp[tmap['regex_name']].search(t.description):
                    self.tag([t.id], [tmap['tag_name']])
        

class RegexManager(Connection):
    """Handles all regex queries"""

    def regex_list(self, with_tags=True, tags_compressed=True):
        """A list of all regexs"""
        with self:
            if with_tags:
                query = (
                    self.db.session.query(Regex, Tag)
                    .join(Regex.tags)
                )
                result = self.query_pd(query)
                result.columns = ['regex_id', 'regex_name', 'tag_id', 'tag_name', 'tag_description']
            else:
                query = self.db.session.query(Regex)
                result = self.query_pd(query)
                result.columns = ['regex_id', 'regex_name']

        if not with_tags:
            return result

        if tags_compressed:
            result = (
                result
                .groupby('regex_name')
                .tag_name.agg([('count', 'count'), ('tag_name', ', '.join)])
            )

        return result

    def regex_exists(self, regex_name):
        """Test if a given regex exists in the database

        :regex_name (str): TODO
        :returns (bool): TODO

        """
        with self:
            regex = self.db.session.query(Regex).filter_by(name=regex_name).one_or_none()

        return regex if regex else False
        
    def add_regex(self, regex):
        """Adds a regex definition"""
        regex = self.regex_exists(regex_name)
        if regex:
            return regex
        with self:
            regex = Regex(name=regex_name)
            self.db.session.add(regex)
            self.db.session.commit()

        return regex

    def link_regex_tag(self, tag_names, regex_names):
        """Links the given tag to a regex

        :tag_name: TODO
        :regex_id: TODO
        :returns: TODO

        """
        tman = TagManager()
        with self:
            for reg in regex_names:
                regex = self.add_regex(reg)
                for t in tag_names:
                    tag = tman.add_tag(t)
                    regex.tags.append(tag)
            self.db.session.commit()
        
    def remove_regex(self, regex):
        """Remove a regex definition"""

    def auto_tag(self, month):
        """Auto tag all transactions in a month against all defined regex"""
        regexs = self.regex_list(with_tags=False).to_dict(orient='records')
        regex = {}
        for r in regexs:
            regex[r['regex_name']] = re.compile(r['regex_name'])

        tag_map = self.regex_list(tags_compressed=False).to_dict(orient='records')
        tm = TransactionManager()
        transactions = tm.untagged(month)

        for i, t in transactions.iterrows():
            for tmap in tag_map:
                if regex[tmap['regex_name']].search(t.description):
                    self.tagTransaction([t.id], [tmap['tag_name']])


class GroupManager(Connection):
    """Handles all group queries"""
        
        
class AccountManager(Connection):
    """Handles all account queries"""

if __name__ == "__main__":
    import datetime as dt
    tm = TransactionManager()
    t = tm.transactions(dt.date(2021,4,1), with_tags=True)
    t2 = tm.untagged(dt.date(2021,4,1))
    
