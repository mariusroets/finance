import json
import pandas as pd
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('mysql://finance:finance@192.168.0.105/finance')
Session = sessionmaker(bind=engine)

class DBEncoder(json.JSONEncoder):
    def default(self, obj):
        """Custom JSON encoder"""
        if isinstance(obj, dt.datetime) or isinstance(obj, dt.date):
            return obj.isoformat()

        if isinstance(obj, decimal.Decimal):
            return float(obj)

        return json.JSONEncoder.default(self, obj)

class QueryRunner():
    """Runs queries and returns data in various formats"""

    def __init__(self):
        """TODO: to be defined1. """
        
    def _toList(self, query):
        """Converts the data to a native python list """
        data = query.all()
        if not data:
            return []
        if isinstance(data[0], Base):
            return [ { c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs} for row in data]
        elif isinstance(data[0], tuple):
            columns = [r['name'] for r in query.column_descriptions]
            return [dict(zip(columns, row)) for row in data]
        

    def execute(self, query, **kwargs):
        """Returns the query, or executes the query and return result based on specified 'returnval' parameter

        :param query: TODO
        :param kwargs: 
            * **returnval** (string) -- Specifies how the results should be returned. Could be one of ['list','dataframe','query','json']. If not specified, returns a SqlAlchemy result proxy. 
            
        :returns: TODO

        """
        returnval = kwargs['returnval'] if 'returnval' in kwargs else None
        if returnval == None:
            return query.all()
        elif returnval == 'list':
            return self._toList(query)
        elif returnval == 'json':
            return json.dumps(self._toList(query), cls=DBEncoder)
        elif returnval == 'dataframe':
            return pd.read_sql(query.statement, query.session.bind)
        elif returnval == 'query':
            return query
        else:
            raise ValueError("Unrecognized returnval parameter")

class Connection:
    """Handles a set of database changes for a specific entity"""

    def __init__(self, session=None):
        """Constructor """
        self._session = None
        if session:
            self._session = session
        else:
            self._session = Session()

    def __del__(self):
        self.close()

    @property
    def session(self):
        """The database session used"""
        return self._session

    def close(self):
        """Close the session"""
        if self._session:
            self._session.close()
            self._session = None

    def query(self, query):
        """Runs a given query and returns a dataframe"""
        qry = QueryRunner()
        
        df = qry.execute(query, returnval='dataframe')

        return df
