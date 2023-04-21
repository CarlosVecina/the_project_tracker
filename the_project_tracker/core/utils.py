from sqlmodel import Session, select

from the_project_tracker.db.conn import AbstractDataConnection
import sqlalchemy


def parse_github_url(github_url: str) -> tuple[str]:
    owner, repo = github_url.strip("/").split("/")[-2:]
    return (owner, repo)


def check_integrity(
    db: AbstractDataConnection, table: sqlalchemy.schema.Table, **kwargs
) -> bool:
    with Session(db.get_engine()) as session:
        statement = select(table)
        statement = statement.filter_by(**kwargs)
        rows = session.exec(statement).first()
    return rows is None
