from .models import Session

class DBManager:
    """Handles a set of database changes for a specific entity"""

    def __init__(self, session=None):
        """Constructor """
        if session:
            self._session = session
        else:
            self._session = Session()

    def __del__(self):
        if self._session:
            self._session.close()

    @property
    def session(self):
        """The database session used"""
        return self._session
