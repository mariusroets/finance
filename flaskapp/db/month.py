from db.models import Transaction
from db.dbmanager import Connection

class Month(Connection):

    def months(self):
        data = self.query(self.session
                   .query(Transaction.effective_month)
                   .distinct()
                   .order_by(Transaction.effective_month))
        return data

if __name__ == "__main__":
    m = Month()
    print(m.months())
