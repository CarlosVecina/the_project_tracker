import datetime

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlmodel import Session, select

from the_project_tracker.core.data_models import (
    ProjectEvolutionTable,
    ProjectTable,
)
from the_project_tracker.core.utils import check_integrity, parse_github_url
from the_project_tracker.db.pg_conn import PGDataConnection
from the_project_tracker.db.sqlite_conn import SQLiteDataConnection

load_dotenv()


def get_tracked_projects(db):
    with Session(db.get_engine()) as session:
        statement = select(ProjectTable)
        statement = statement.filter_by(activated=True, revised=True)
        projects = session.exec(statement).fetchall()
    return projects


# TODO: create a discovery pipeline that inserts toProject entities
# (with all the fields including project image that is tbimplemented)
# and not to the Evolution. Then the evolution pipeline will only
# have one project source that will be the Project table and insert into
# Evolution entity.
class DiscoveryTopProjectEvolutionPipeline(BaseModel):
    class Config:
        title = "Top Project Evolution by lang evolution"
        arbitrary_types_allowed = True

    languages: list[str] = ["python", "R"]
    n: int = 100
    # TODO: workaround 'retries' for: Github api sort is not working?
    pages: int = 6
    connection: PGDataConnection | SQLiteDataConnection = PGDataConnection()

    def run(self):
        [self.get_top_n_projects(lang, self.n, self.pages) for lang in self.languages]

    @classmethod
    def get_top_n_projects(cls, lang: str, n: int, pages: int):
        for p in range(0, pages):
            response = requests.get(
                f"https://api.github.com/search/repositories?q=language:{lang}&sort=stars&per_page={n}",
                headers={"Accept": "application/vnd.github.preview"},
            ).json()

            db = PGDataConnection()
            db.connect()
            today = datetime.date.today()

            for proj in response["items"]:
                integrity = check_integrity(
                    db=db,
                    table=ProjectEvolutionTable,
                    project_fullname=proj["full_name"],
                    date=today,
                )
                if not integrity:
                    continue

                project_snapshot = ProjectEvolutionTable(
                    date=today,
                    project_name=proj["name"],
                    project_fullname=proj["full_name"],
                    forks_count=proj["forks_count"],
                    stargazers_count=int(proj["stargazers_count"]),
                    watchers_count=proj["watchers_count"],
                    # subscribers_count=proj["subscribers_count"],
                    open_issues=proj["open_issues"],
                    inserted_at=datetime.datetime.now(),
                )
                with Session(db._conn) as session:
                    session.add(project_snapshot)
                    session.commit()


class ProjectEvolutionPipeline(BaseModel):
    class Config:
        title = "Project Evolution Monitoring"
        arbitrary_types_allowed = True

    connection: PGDataConnection | SQLiteDataConnection = PGDataConnection()
    repo_url: str | None

    def run(self):
        db = self.connection
        today = datetime.date.today()

        if self.repo_url:
            active_projects = [self.repo_url]
        else:
            active_projects: list[ProjectTable] = get_tracked_projects(db)

        for project in active_projects:
            owner, repo = parse_github_url(project.project_url)

            integrity = check_integrity(
                db=db, table=ProjectEvolutionTable, project_name=repo, date=today
            )
            if not integrity:
                continue

            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={"Accept": "application/vnd.github.preview"},
            ).json()
            project_snapshot = ProjectEvolutionTable(
                date=today,
                project_name=response["name"],
                project_fullname=response["full_name"],
                forks_count=response["forks_count"],
                stargazers_count=response["stargazers_count"],
                watchers_count=response["watchers_count"],
                subscribers_count=response["subscribers_count"],
                open_issues=response["open_issues"],
                inserted_at=datetime.datetime.now(),
            )
            with Session(db._conn) as session:
                session.add(project_snapshot)
                session.commit()
