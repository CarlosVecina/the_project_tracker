from typing import ClassVar, Literal

import pandas as pd
import sqlalchemy as sa
import sqlalchemy as db
from pydantic import BaseSettings, Field, SecretStr
from sqlalchemy.engine.url import URL
from sqlalchemy.sql import text as sqla_text
from sqlmodel import SQLModel
from the_project_tracker.core.data_models import *  # nopycln: import # load table=True entities

from the_project_tracker.db.conn import AbstractDataConnection
from the_project_tracker.db.utils import create_upsert_method
from sshtunnel import SSHTunnelForwarder


class SettingsSSH(BaseSettings):
    class Config:
        title = "SSH connection config"
        env_prefix = "SSH_"
        case_sensitive = False

    user: str | None = Field(None, description="Database username")
    pwd: SecretStr | None = Field(None, description="Database username")


class PGDataConnection(BaseSettings, AbstractDataConnection):
    class Config:
        title = "Postgres (SQLAlchemy) Data Connection"
        env_prefix = "PG_"
        case_sensitive = False
        underscore_attrs_are_private = True

    ssh_config: SettingsSSH | None = None
    _local_host: str | None = None
    _local_port: int | None = None

    host: str = Field(..., description="Database Host")
    port: int | None = Field(None, description="Database connection port number")

    database: str = Field(..., description="Database name to connect to")

    username: str | None = Field(None, description="Database username")
    pwd: SecretStr | None = Field(None, description="Database password")

    write_chunksize: int = 2000

    schema: ClassVar[str] = "project_tracker"

    @property
    def connection_str(self) -> URL:
        if self.ssh_config:
            server = SSHTunnelForwarder(
                (self.host, 22),
                ssh_username=self.ssh_config.user,
                ssh_password=self.ssh_config.pwd.get_secret_value(),
                remote_bind_address=("localhost", self.port),
            )
            server.start() #start ssh server
            self._local_port = server.local_bind_port
            self._local_host = "localhost"

        connection_url = URL.create(
            drivername="postgresql+psycopg2",
            host=self._local_host if self._local_host is not None else self.host,
            port=self._local_port if self._local_port is not None else self.port,
            database=self.database,
            username=self.username,
            password=None if self.pwd is None else self.pwd.get_secret_value(),
        )

        return connection_url

    def create_connectable_or_pass(self) -> None:
        "Connects to the Database"
        if not self._conn:
            self._conn = sa.create_engine(
                self.connection_str,
                connect_args={"options": "-csearch_path={}".format(self.schema)},
            )

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
        self.create_connectable_or_pass()

        data = pd.read_sql(
            sqla_text(query, bind=self._conn),
            con=self._conn,
            params=kwargs,
            chunksize=None,
        )

        return data

    def create_db_if_not_exists(self) -> None:
        """SQLModel create all entities that are configured as table=True"""
        self.create_connectable_or_pass()
        SQLModel.metadata.create_all(self._conn)


if __name__ == "__main__":
    # Expects at least PG_HOST, PG_PORT, PG_DATABASE, PG_USERNAME and PG_PWD
    # from the env
    from dotenv import load_dotenv
    load_dotenv()

    con = PGDataConnection(ssh_config=SettingsSSH())
    con.create_db_if_not_exists()
