import sqlite3
from abc import abstractmethod
from typing import ClassVar

import pandas as pd
import sqlalchemy
from pydantic import BaseModel

from the_project_tracker.core.data_models import PR, Documentation, Project, Release


class AbstractDataConnection(BaseModel):
    class Config:
        title = "Abstract Data Connection"
        underscore_attrs_are_private = True

    prs_table: ClassVar[str] = "prs"
    releases_table: ClassVar[str] = "releases"
    projects_table: ClassVar[str] = "projects"
    documentations_table: ClassVar[str] = "documentations"

    _conn: sqlalchemy.engine.Connectable | sqlite3.Connection | None = None

    @abstractmethod
    def create_connectable_or_pass(self):
        ...

    @abstractmethod
    def create_db_if_not_exists(self):
        raise NotImplementedError

    def insert_pr(self, pr: PR, if_exists: str = "append") -> None:
        self.create_connectable_or_pass()

        df = pd.DataFrame([pr.dict()])
        df.to_sql(self.prs_table, self._conn, if_exists=if_exists, index=False)
        print("PR inserted")

    def insert_release(self, release: Release, if_exists: str = "append") -> None:
        self.create_connectable_or_pass()

        df = pd.DataFrame([release.dict()])
        df.to_sql(self.releases_table, self._conn, if_exists=if_exists, index=False)
        print("Release inserted")

    def instert_project(self, project: Project, if_exists: str = "append") -> None:
        self.create_connectable_or_pass()

        df = pd.DataFrame([project.dict()])
        df.to_sql(self.projects_table, self._conn, if_exists=if_exists, index=False)
        print("Project inserted")

    def insert_documentation(self, documentation: Documentation, if_exists: str = "append") -> None:
        self.create_connectable_or_pass()

        df = pd.DataFrame([documentation.dict()])
        df.to_sql(self.documentations_table, self._conn, if_exists=if_exists, index=False)
        print("Documentation inserted")