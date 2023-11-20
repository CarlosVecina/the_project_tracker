import datetime
import os
from pandas import DataFrame
import streamlit as st
from dotenv import load_dotenv
from markdownlit import mdlit
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from streamlit_pills import pills
from the_project_tracker.db.sqlite_conn import SQLiteDataConnection
from utils import Categories, format_output_text, load_css

from the_project_tracker.core.data_models import Project, ProjectTable
from the_project_tracker.core.github_retriever import GitHubRetrieverProjects
from the_project_tracker.core.utils import parse_github_url
from the_project_tracker.db.pg_conn import PGDataConnection, SettingsSSH

# TODO: As pydantic config. object to set in a YAML file
NUM_COLS = 1
N_ELEMENTS = 5
TAG_ALL_LANG = "-ALL-"
TAG_EXPLANATION = "explanation"
AUTO_REVIEW_NEW_PROJECT = False


# Base de datos
load_dotenv()
if os.getenv('LOCAL_DB') is not None:
    db = SQLiteDataConnection(db_name=os.getenv('LOCAL_DB'))
    SCHEMA=""
    @st.cache_data(ttl=12 * 3600, show_spinner=False)
    def get_projectos():
        return db.run_query(
            f"""
        select *
        from {SCHEMA}projects
        where activated = True and revised = True;
        """
        )
else:
    db = PGDataConnection(ssh_config=SettingsSSH())
    SCHEMA = "project_tracker."
    @st.cache_data(ttl=12 * 3600, show_spinner=False)
    def get_projectos():
        with Session(db.get_engine()) as session:
            statement = select(ProjectTable)
            if not AUTO_REVIEW_NEW_PROJECT:
                statement = statement.filter_by(activated=True, revised=True)
            projects = session.exec(statement).fetchall()
        return projects

# Configuración Página
st.set_page_config(
    page_title="Releases - OSPT",
    page_icon="🔎",
    menu_items={
        "Get Help": "https://www.linkedin.com/in/carlos-vecina/",
    },
)

# Estilos
css = load_css()
st.markdown(css, unsafe_allow_html=True)


def icon(emoji: str):
    st.write(
        f'<span style="font-size: 38px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


# Acceso a datos
if "limit" not in st.session_state:
    st.session_state["limit"]: int = 60

if "df_releases" not in st.session_state:
    st.session_state["df_releases"]: DataFrame = db.run_query(
        f"""
    select *
    from (
    select * , ROW_NUMBER() OVER (PARTITION BY repo_url order by published_at DESC) AS r
    from {SCHEMA}releases
    ) ord
    where ord.r <= {N_ELEMENTS}"""
    )

if "df_prs" not in st.session_state:
    st.session_state["df_prs"]: DataFrame = db.run_query(
        f"""
    select *
    from (
    select * , ROW_NUMBER() OVER (PARTITION BY repo_url order by merged_at DESC) AS r
    from {SCHEMA}prs
    ) ord
    where ord.r <= {N_ELEMENTS};
    """
    )

st.write(
    '<style>[data-testid="stImage"] img {border: 1px solid #D6D6D9; border-radius: 3px; height: 200px; object-fit: cover; width: 100%} .block-container img:hover {}</style>',
    unsafe_allow_html=True,
)

# Title
icon("🔎")

"""
# OSPT - Open Source Project Tracking
"""

description = st.empty()
description.write(
    f"""
## **Stay up to date with your favorite libraries!** 

The information provided here is automated through daily access to projects on GitHub and explanation by ChatGPT4.
"""
)
if "new_project" not in st.session_state:
    st.session_state["new_project"] = ""


# New Project
def get_new_project():
    msg_nuevo_proy = "<span style='color:green'>Congratulations! We have received your request and the project will be added shortly.</span>"
    if st.session_state["new_project"] != "":
        try:
            owner, repo = parse_github_url(st.session_state["new_project"])
        except:
            st.write(
                "Invalid URL de GitHub. Example format: https://github.com/streamlit/streamlit"
            )
        gh = GitHubRetrieverProjects(owner=owner, repo=repo)
        # TODO: automatizar 100%: get_google_url_img_proyecto(repo)
        proy = Project(
            project_name=repo,
            project_url=st.session_state["new_project"],
            project_source="github",
            stars=gh.get_project_stars(),
            program_language=gh.get_project_language(),
            author=gh.get_project_author(),
            description=gh.get_project_description(),
            inserted_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            activated=False,
            revised=False,
        )
        try:
            db.instert_project(proy)
        except Exception as e:
            if type(e) == IntegrityError:
                msg_nuevo_proy = f"<span style='color:green'>This project: {repo.upper()} has already been recently included or waiting to be included! :)</span>"
        st.markdown(msg_nuevo_proy, unsafe_allow_html=True)


new_project = st.text_input(
    "Can't find a module? **URL of the new project to follow.** Whatever the programming language may be.",
    placeholder="p.ej. https://github.com/streamlit/streamlit",
    key="new_project",
    on_change=get_new_project(),
)


st.write(
    """
\n
***"""
)

# Panel de búsqueda
col1, col2, col3 = st.columns([2, 1, 1])
search = col1.text_input(
    "Search Terms", placeholder="e.g tidyverse, validation, charts"
)

select_leguaje = col2.selectbox(
    "Language", ["Python", "R", TAG_ALL_LANG], index=2
)
select_orden = col3.selectbox("Sort by", ["⭐️ Stars", "🚀 Recency"])

category = pills(
    "Category",
    [i.name for i in Categories],
    [i.icon for i in Categories],
    index=None,
    format_func=lambda x: Categories.__getitem__(x).value,
    label_visibility="collapsed",
)
st.write("")


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


@st.cache_data(ttl=12 * 3600, show_spinner=False)
def sort_projects(_projects: list, by: str):
    if by == "⭐️ Stars":
        return sorted(
            _projects,
            key=lambda c: (
                int(c.stars) if c.stars is not None else 0,
                c.image_url is not None,  # items with image first
            ),
            reverse=True,
        )
    elif by == "🚀 Recency":
        return sorted(
            _projects,
            key=lambda c: (
                c.created_at
                if c.created_at is not None
                else datetime.datetime(1970, 1, 1),
                c.image_url is not None,  # items with image first
            ),
            reverse=True,
        )
    else:
        raise ValueError("`by` must by 'Stars' or 'Recency'")


@st.cache_data(ttl=12 * 3600, show_spinner=False)
def filter_projects(
    _projects, language: str = None, search: str = None, category: str = None
):
    if language and language != TAG_ALL_LANG:
        _projects = list(filter(lambda c: language in c.program_language, _projects))
    if search:
        _projects = list(
            filter(lambda c: search.lower() in c.search_text, _projects)
        )
    if category:
        _projects = list(
            filter(
                lambda c: (category in c.category) | (category in c.subcategory),
                _projects,
            )
        )
    return _projects


def shorten(text, length: int = 150):
    if len(text) > length:
        short_text = text[:length]

        if short_text[-1] != " " and text[length] != " ":
            short_text = short_text[: short_text.rfind(" ")]

        short_text = short_text.rstrip()

        if short_text[-1] in [".", "!", "?"]:
            return short_text
        elif short_text[-1] in [",", ";", ":", "-"]:
            return short_text[:-1] + "..."
        else:
            return short_text + "..."
    else:
        return text


# @st.cache_data
def show_projects(_projects: list, limit: int | None = None):
    if limit is not None:
        _projects = _projects[:limit]

    for i, proyectos_chunk in enumerate(chunks(_projects, NUM_COLS)):
        cols = st.columns(NUM_COLS, gap="medium")
        for c, col in zip(proyectos_chunk, cols):
            with col:
                if c.image_url is not None:
                    img_path = c.image_url
                else:
                    img_path = "https://streamlit.io/sharing-image-facebook.jpg"

                st.image(str(img_path), use_column_width=True)
                title = f"#### {c.project_name}"
                if c.stars:
                    title += f" ({int(c.stars)} ⭐️)"
                if c.last_release:
                    title += f" - Última Release: {c.last_release}"
                st.write(title)
                if c.author_avatar_url:
                    avatar_path = c.author_avatar_url
                if c.author and c.author_avatar_url:
                    st.caption(
                        f'<a href="https://github.com/{c.author}"><img src="{avatar_path}" style="border: 1px solid #D6D6D9; width: 20px; height: 20px; border-radius: 50%"></a> &nbsp; <a href="https://github.com/{c.author}" style="color: inherit; text-decoration: inherit">{c.author}</a>',
                        unsafe_allow_html=True,
                    )
                if c.description:
                    st.write(shorten(c.description))
                formatted_links = []
                if c.project_url:
                    formatted_links.append(f"@(GitHub)({c.project_url})")

                st.write("**Last Releases**")
                df = st.session_state["df_releases"]

                exp = True
                for _, e in df[df.repo_url == c.project_url].iterrows():
                    with st.expander(e["name"], expanded=exp):
                        out = format_output_text(e[TAG_EXPLANATION])
                        st.text(out)
                        exp = False

                #st.write("**Últimas PRs mergeadas**") #TODO: Ver como añadirlo sin ser tan verbose

                mdlit(" &nbsp;•&nbsp; ".join(formatted_links))
                st.write("")
                st.write("")
                st.write("")


def show_more():
    st.session_state["limit"] += 40


# Listado y filtro de Proyectos
proyectos = get_projectos()
if proyectos is None:
    proyectos = []
proyectos = sort_projects(proyectos, select_orden)
proyectos = filter_projects(proyectos, select_leguaje, search, category)

if not search and not category and select_orden == "🚀 Recency":
    "## 🚀 Releases from last weeks!"
    st.write("")
    df_ultimas_releases = st.session_state["df_releases"]
    df_ultimas_releases = (
        df_ultimas_releases[
            (df_ultimas_releases.repo_url.isin([i.project_url for i in proyectos]))
            & (
                df_ultimas_releases.published_at
                > str(datetime.datetime.now() - datetime.timedelta(days=14))
            )
        ]
        .sort_values("published_at", ascending=False)
        .head(5)
    )
    exp_ultimas_real = True
    for _, e in df_ultimas_releases.iterrows():
        _, repo = parse_github_url(e["repo_url"])
        with st.expander(f'{repo} - Release: {e["name"]}', expanded=exp_ultimas_real):
            out = format_output_text(e[TAG_EXPLANATION])
            st.text(out)
    "## 🌟 Favs"

st.write("")
st.write("")

show_projects(proyectos, st.session_state["limit"])

if len(proyectos) > st.session_state["limit"]:
    st.button("Show more projects", on_click=show_more, type="primary")
