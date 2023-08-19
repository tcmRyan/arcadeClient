from sqlalchemy import create_engine, orm


class DB:
    session: orm.scoped_session

    def __init__(self, conn: str = None):
        self.session = None
        self.conn_str = conn
        self._engine = None
        self._conn = None

    @property
    def engine(self):
        if self._engine is None and self.conn_str:
            self._engine = create_engine(self.conn_str)

        return self._engine

    def config(self, conn: str):
        """
        Connection string that re-initializes the engine and session
        :param conn:
        :return:
        """
        self.conn_str = conn

        if self._conn is not None:
            self._conn.close()

        self.create_session()

    def create_session(self):
        if self.engine is not None:
            self._conn = self.engine.connect()
            session = orm.scoped_session(orm.sessionmaker())
            self.session = session(bind=self.engine)
        else:
            print("Session not created, no connection string")
            self.session = ...

    def __enter__(self):
        self.create_session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
