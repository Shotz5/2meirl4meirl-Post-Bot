import sqlite3

class Database:
    def __init__(self, name):
        self._conn = sqlite3.connect(name);
        self._cursor = self._conn.cursor();

    def __enter__(self):
        return self;

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close();

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor;

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params = None):
        return self.cursor.execute(sql, params or ());

    def fetchAll(self):
        return self.cursor.fetchall();

    def fetchOne(self):
        return self.cursor.fetchone();

    def query(self, sql, params=None, fetchOne=False):
        self.cursor.execute(sql, params or ());
        res = self.fetchAll();
        if (len(res) == 1 or fetchOne):
            return res[0];
        else:
            return res;