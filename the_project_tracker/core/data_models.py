import datetime

from sqlmodel import Field, SQLModel


class PR(SQLModel):
    repo_url: str = Field(primary_key=True)
    pr_id: str = Field(primary_key=True)
    inc_code_diffs: int = Field(primary_key=True)
    merged_at: str
    pr_title: str
    pr_body: str | None = Field(nullable=True)
    commits_url: str
    explanation: str
    explanation_es: str
    inserted_at: str
    updated_at: str


class PRTable(PR, table=True):
    __tablename__: str = "prs"


class Release(SQLModel):
    repo_url: str = Field(primary_key=True)
    name: str
    tag_name: str = Field(primary_key=True)
    published_at: str
    assets: str
    body: str
    explanation: str | None
    explanation_es: str | None
    inserted_at: str
    updated_at: str


class ReleaseTable(Release, table=True):
    __tablename__: str = "releases"


class Project(SQLModel):
    project_name: str = Field(primary_key=True)
    project_url: str = Field(primary_key=True)
    project_source: str
    stars: int
    description: str
    created_at: datetime.datetime | None = Field(nullable=True)
    inserted_at: datetime.datetime
    updated_at: datetime.datetime
    image_url: str | None = Field(nullable=True)
    search_text: str | None = Field(nullable=True)
    author: str | None = Field(nullable=True)
    program_language: str | None = Field(nullable=True)
    category: str | None = Field(nullable=True)
    subcategory: str | None = Field(nullable=True)
    author_avatar_url: str | None = Field(nullable=True)
    last_release: str | None = Field(nullable=True)
    last_release_at: str | None = Field(nullable=True)
    release_notes: str | None = Field(nullable=True)
    activated: bool
    revised: bool

    def __hash__(self) -> int:
        return Project.__hash__(self)


class ProjectTable(Project, table=True):
    __tablename__: str = "projects"


class Documentation(SQLModel):
    project_name: str = Field(primary_key=True)
    project_version: str = Field(primary_key=True)
    doc_obj: str | None = Field(primary_key=True)
    doc_method: str | None = Field(primary_key=True)
    doc_content: str 
    doc_content_interpretation: str | None
    inserted_at: datetime.datetime
    updated_at: datetime.datetime

    def __hash__(self) -> int:
        return Project.__hash__(self)


class DocumentationTable(Project, table=True):
    __tablename__: str = "documentations"
