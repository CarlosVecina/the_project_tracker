import sqlite3
from contextlib import closing

from the_project_tracker.db.conn import AbstractDataConnection
from the_project_tracker.db.utils import DDL_PRS, DDL_RELEASES


class SQLiteDataConnection(AbstractDataConnection):
    class Config:
        title = "SQLite local Data Connection"
        underscore_attrs_are_private = True

    db_name: str

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        self._conn = conn

    def query_database(self, query: str, search_text: str) -> list[str]:
        if not self._conn:
            self.connect()
        cur = self._conn.cursor()
        cur.execute(query, (*search_text,))
        rows = cur.fetchall()
        return rows

    def create_db_if_not_exists(self):
        if not self._conn:
            self.connect()

        with closing(self._conn.cursor()) as cur:
            cur.execute(DDL_PRS)
            cur.execute(DDL_RELEASES)

    def execute(self, transaction: str) -> None:
        with closing(self._conn.cursor()) as cur:
            cur.execute(transaction)


if __name__ == "__main__":
    con = SQLiteDataConnection(db_name="tracker_db.sqlite")
    con.create_db_if_not_exists()
