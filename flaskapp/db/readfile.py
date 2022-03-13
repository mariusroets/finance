import pandas as pd
import hashlib
import datetime
from analysis.models import Account, Transaction, Session
from sqlalchemy.exc import IntegrityError

class ReadFile(object):

    """Reads CSV file into database"""

    def __init__(self, filename):
        """Constructor

        :filename: TODO

        """
        self._filename = filename
        self.df = None
        
    def read(self):
        """Reads the file into the database
        :returns: TODO

        """
        self.df = pd.read_csv(self._filename)
        self.df.Date = self.df.Date.astype('str')
        self.df.Date = pd.to_datetime(self.df.Date, format='%Y%m%d')

    def save(self, account_name):
        """Saves the data to the database

        :session: TODO
        :returns: TODO

        """
        session = Session()
        acc = session.query(Account).filter_by(name = account_name).first()
        l = []
        for i, row in self.df.iterrows():
            month = datetime.date(row[0].year, row[0].month, 1)
            l.append(Transaction(date = row[0], description = row[1], amount = row[2],\
                    balance=row[3], effective_month=month, account=acc))
            l[-1].createHash()

        for t in l:
            try:
                session.add(t)
                session.commit()
            except IntegrityError as e:
                print("Skipped")
                print(t)
                session.rollback()

if __name__ == "__main__":
    r = ReadFile('data/transactionHistory (15).csv')
    r.read()
    #r.save(session, 'Cheque') 
