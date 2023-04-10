from typing import ClassVar, Literal

import pandas as pd
import sqlalchemy as sa
import sqlalchemy as db
from pydantic import BaseSettings, Field, SecretStr
from sqlalchemy.engine.url import URL
from sqlalchemy.sql import text as sqla_text

from the_project_tracker.db.conn import AbstractDataConnection
from the_project_tracker.db.utils import DDL_PRS, DDL_RELEASES, create_upsert_method


class PGDataConnection(BaseSettings, AbstractDataConnection):
    class Config:
        title = "Postgres (SQLAlchemy) Data Connection"
        env_prefix = "PG_"
        case_sensitive = False
        underscore_attrs_are_private = True

    host: str = Field(..., description="Database Host")
    port: int | None = Field(None, description="Database connection port number")

    database: str = Field(..., description="Database name to connect to")

    username: str | None = Field(None, description="Database username")
    pwd: SecretStr | None = Field(None, description="Database password")

    write_chunksize: int = Field(
        1000,
        description="the number of rows in each batch to be written at a time",
        example=1000,
    )

    schema: ClassVar[str] = "project_tracker"

    @property
    def connection_str(self) -> URL:
        s_pwd = None if self.pwd is None else self.pwd.get_secret_value()
        connection_url = URL.create(
            drivername="postgresql+psycopg2",
            host=self.host,
            port=self.port,
            database=self.database,
            username=self.username,
            password=s_pwd,
        )
        return connection_url

    def connect(self) -> None:
        "Connects to the Database"
        if not self._conn:
            self._conn = sa.create_engine(
                self.connection_str,
                connect_args={"options": "-csearch_path={}".format(self.schema)},
            )
        else:
            None

    def disconnect(self) -> None:
        "Disconnects from the Database"
        if self._conn:
            conn = self._conn.connect()
            conn.invalidate()
            self._conn.dispose()
            self._conn = None

    def get_engine(self) -> sa.engine:
        if not self._conn:
            self._conn = sa.create_engine(
                self.connection_str,
                connect_args={"options": "-csearch_path={}".format(self.schema)},
            )
        return self._conn

    def query_database(self, query: str, search_text: str) -> list[str]:
        if not self._conn:
            self.connect()
        cur = self._conn.cursor()
        cur.execute(query, (*search_text,))
        rows = cur.fetchall()
        return rows

    def write_table(
        self,
        tablename: str,
        df: pd.DataFrame,
        if_exists: Literal["append", "replace", "fail"] = "append",
        upsert_col: str | None = None,
    ) -> int | None:
        if upsert_col:
            # create DB metadata object that can access table names, primary keys, etc.
            meta = db.MetaData(self._conn)

            # dictionary which will add additional changes on update statement. I.e. all the columns which are not present in DataFrame,
            # but needed to be updated regardless. The common example is `updated_at`. This column can be updated right on SQL server, instead of in pandas DataFrame
            extra_update_fields = {upsert_col: "NOW()"}
            # extra_update_fields = {}

            # create upsert method that is accepted by pandas API
            method = create_upsert_method(meta, extra_update_fields)
        else:
            method = "multi"

        n_rows = df.to_sql(
            tablename,
            self._conn,
            # schema=schema,
            if_exists=if_exists,
            method=method,
            index=False,
            chunksize=self.write_chunksize,
        )

        return f"Inserted {int(n_rows)}."

    def run_query(self, query: str, **kwargs) -> pd.DataFrame:
        self.connect()

        data = pd.read_sql(
            sqla_text(query, bind=self._conn),
            con=self._conn,
            params=kwargs,
            chunksize=None,
        )

        return data

    def create_db_if_not_exists(self) -> None:
        with self._conn.connect() as conn:
            conn.execute(DDL_PRS)
            conn.execute(DDL_RELEASES)

    def query_database(self, query: str) -> list[str]:
        if not self._conn:
            self.connect()

        with self._conn.connect() as conn:
            results = conn.execute(query)
            rows = results.fetchall()
            return rows
