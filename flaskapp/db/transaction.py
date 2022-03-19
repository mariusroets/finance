import re
import pandas as pd
from sqlalchemy.orm.exc import NoResultFound
import datetime as dt
from .models import *
from .dbmanager import Connection
from .autotags import AutoTags
from .tags import Tags

class TransactionManager(Connection):

    """Manages everything related to transactions""" 

    def __init__(self, month=None):
        """Constructor """
        super().__init__()
        self._month = month
        self._tags = Tags()
        self._autotags = AutoTags()

    @property
    def month(self):
        """The month for which the transaction analysis is done"""
        return self._month

    def auto_tag(self):
        """Automatically tag all transactions
        :returns: TODO

        """
        regexs = self.session.query(Regex).all()
        regex = {}
        for r in regexs:
            regex[r.name] = re.compile(r.name)

        tag_map = self.session.query(Regex, Tag).join(Regex.tags).all()
        transactions = self.untagged()
        for i, t in transactions.iterrows():
            for tm in tag_map:
                if regex[tm[0].name].search(t.description):
                    self.tagTransaction([t.id], [tm[1].name])

    def tagTransaction(self, transaction_ids, tag_names):
        """Attaches a tag to the specified transaction

        :transaction_id: TODO
        :tag_name: TODO
        :returns: TODO

        """
        for trans in transaction_ids:
            try:
                transaction = self.session.query(Transaction).filter_by(id = trans).one()
            except NoResultFound:
                print("Transaction does not exist")
                continue
            for t in tag_names:
                tag = self._tags.add_tag(t)
                transaction.tags.append(tag)
            
        self.session.commit()

    def removeTag(self, transaction_id, tag_name):
        """Remove the given tag from the transaction specified

        :transaction_id: TODO
        :tag_name: TODO
        :returns: TODO

        """
        trans = self.session.query(Transaction).get(transaction_id)
        trans.tags = list(filter(lambda t: t.name != tag_name, trans.tags))
        self.session.commit()

    def transactions(self):
        """Return dataframe of all transactions for a month, or all if month not specified

        :returns: TODO

        """
        q = self.session.query(Transaction, Account).join(Transaction.account).with_labels()
        if self.month:
            q = q.filter(Transaction.effective_month == self.month)

        df = pd.read_sql(q.statement, self.session.bind).\
            drop(columns=[
                'transaction_key',
                'transaction_effective_month',
                'transaction_balance', 
                'transaction_account_id',
                'account_id']).\
            rename(columns={
                'transaction_id':'id',
                'transaction_date': 'date',
                'transaction_amount': 'amount',
                'transaction_description': 'description',
                'account_name': 'account'})
        df.date = pd.to_datetime(df.date)
        return df

    def untagged(self):
        """Return untagged transactions for given month or all untagged 
            transactions if month not specified
        :returns: TODO
        """
        q = self.session.query(Transaction, Account, Tag).\
                join(Transaction.account).\
                outerjoin(Transaction.tags).\
                with_labels().\
                filter(Tag.name == None)
        if self.month:
            q = q.filter(Transaction.effective_month == self.month)

        df = pd.read_sql(q.statement, self.session.bind).\
            drop(columns=[
                'transaction_key',
                'transaction_effective_month',
                'transaction_balance', 
                'transaction_account_id',
                'account_id',
                'tag_id',
                'tag_description']).\
            rename(columns={
                'transaction_id':'id',
                'transaction_date': 'date',
                'transaction_amount': 'amount',
                'transaction_description': 'description',
                'account_name': 'account',
                'tag_name': 'tag'})
        return df

    def expenseIncomeTagged(self):
        """Ensure that all transactions are tagged with one of expense/income/transfer
        :returns: TODO

        """
        df = self.transactionTagFilter(['expense','transfer','income'])
        df = df.drop(columns=['tag'])
        if df.duplicated().any():
            print("Error: The following transactions were multi-tagged:")
            print(df[df.duplicated()])
            return (False, df[df.duplicated()])
        df2 = self.transactions()
        if not df.equals(df2):
            df3 = pd.concat([df, df2]).drop_duplicates(keep=False)
            print("Some transactions have not been tagged expense/income/transfer")
            print(df3)
            return (False, df3)

        return (True, df)

    def transactionTagFilter(self, tags, and_=False):
        """Returns a list of transactions that match the given list of tags

        :tags: TODO
        :returns: TODO

        """
        query = self.session.query(Transaction, Account, Tag).\
            join(Transaction.account).\
            outerjoin(Transaction.tags).\
            filter(Tag.name.in_(tags)).\
            with_labels()
        if self.month:
            query = query.filter(Transaction.effective_month == self.month)

        df = pd.read_sql(query.statement, self.session.bind).\
            drop(columns=[
                'transaction_key',
                'transaction_balance', 
                'transaction_effective_month',
                'transaction_account_id',
                'account_id',
                'tag_id',
                'tag_description'])
        df.columns = ['id', 'date', 'amount', 'description', 'account', 'tag']
        df.date = pd.to_datetime(df.date)
        if (not and_) or (len(tags) == 1):
            return df
        df = df.drop(columns=['tag'])
        df = df[df.duplicated()]
        return df

    def budget(self):
        """Returns a budget based on the months expenses"""
        mfxd = self.transactionTagFilter(['expense', 'monthly_fixed'], True)
        homeloan = self.transactionTagFilter(['transfer', 'monthly_fixed'], True)
        mvar = self.transactionTagFilter(['expense', 'monthly_variable'], True)
        mgrp = self.transactionTagFilter(['expense', 'monthly_group'], True)
        to_remove = self.transactionTagFilter(['expense', 'homeloan'], True)
        mall = self.transactionTagFilter(['expense']).drop(columns=['tag'])
        salary = self.transactionTagFilter(['income', 'salary'], True).amount.sum()
        rent = self.transactionTagFilter(['income', 'rent'], True).amount.sum()
        other = pd.concat([mall, mgrp, mvar, mfxd, to_remove]).drop_duplicates(keep=False)
        return {
            'homeloan': homeloan.amount.sum(),
            'fixed': mfxd.amount.sum(),
            'variable': mvar.amount.sum(),
            'group': mgrp.amount.sum(),
            'other': other.amount.sum(),
            'salary': salary,
            'rent': rent,
            'total_monthly': homeloan.amount.sum() + mfxd.amount.sum() + mvar.amount.sum() + mgrp.amount.sum(),
            'total_expense': homeloan.amount.sum() + mfxd.amount.sum() + mvar.amount.sum() + mgrp.amount.sum() + other.amount.sum(),
            'total_income': salary + rent,
            'budget_deviation': homeloan.amount.sum() + mfxd.amount.sum() + mvar.amount.sum() + mgrp.amount.sum() + salary + rent,
            'actual_deviation': homeloan.amount.sum() + mfxd.amount.sum() + mvar.amount.sum() + mgrp.amount.sum() + other.amount.sum() + salary + rent,
        }

    def transferBalanceReport(self):
        """Checks that transfers balance and return list of transfers
        :returns: TODO

        """
        df = self.transactionTagFilter(['transfer'])
        return (sum(df.amount), df)

    def transactionTags(self, transaction_id, csv=False):
        """Returns a list of tags associated with the given transaction

        :transaction_id: TODO
        :returns: TODO
        """
        query = self.session.query(Transaction, Account, Tag).\
            join(Transaction.account).\
            outerjoin(Transaction.tags).\
            filter(Transaction.id == transaction_id).\
            with_labels()

        df = pd.read_sql(query.statement, self.session.bind).\
            drop(columns=[
                'transaction_key',
                'transaction_balance', 
                'transaction_effective_month',
                'transaction_account_id',
                'account_id',
                'tag_id',
                'tag_description'])
        df.columns = ['id', 'date', 'amount', 'description', 'account', 'tag']
        if csv:
            if df.tag[0] == None:
                return ''
            else:
                return ",".join(df.tag)
        return df
        
    def transactionsWithTags(self):
        """Returns transactions with tag list
        :returns: TODO
        """
        t = self.transactions()
        t['tags'] = ''
        for i, row in t.iterrows():
            tags = self.transactionTags(row['id'], True)
            t.loc[i, 'tags'] = tags

        return t

if __name__ == "__main__":
    tm = TransactionManager(dt.date(2018,8,1))
