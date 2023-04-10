import datetime
from typing import List
from sqlalchemy.exc import IntegrityError
import streamlit as st
from markdownlit import mdlit
from streamlit_pills import pills

from st_app.utils import Categorias, format_output_text, get_google_url_img_proyecto
from the_project_tracker.core.data_models import Project, ProjectTable, PRTable
from the_project_tracker.core.github_retriever import GitHubRetrieverProjects
from the_project_tracker.core.utils import parse_github_url
from the_project_tracker.db.pg_conn import PGDataConnection

st.set_page_config(
    page_title="Releases - OSPT",
    page_icon="👋",
    menu_items={
        "Get Help": "https://www.linkedin.com/in/carlos-vecina/",
    },
)

NUM_COLS = 1
NUM_HISTORICO = 5
TAG_TODOS_LENGUAJES = "-TODOS-"
AUTO_REVIEW_NEW_PROJECT = False

from dotenv import load_dotenv

load_dotenv()
db = PGDataConnection()
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Styles
st.markdown(
    """<style>.st-dn {
border-color: rgba(49, 51, 63, 0.2);
background: #a7eba42e;
}</style>""",
    unsafe_allow_html=True,
)
st.markdown(
    """
<style>
.streamlit-expanderHeader p{
    font-weight: bold;
}
</style>
""",
    unsafe_allow_html=True,
)

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


st.write(
    '<style>[data-testid="stImage"] img {border: 1px solid #D6D6D9; border-radius: 3px; height: 200px; object-fit: cover; width: 100%} .block-container img:hover {}</style>',
    unsafe_allow_html=True,
)

icon("🕵️")
"""
# OSPT - Seguimiento de proyectos Open Source
"""

description = st.empty()
description.write(
    f"""
¡Mantente al día de tus librerías Open Source favoritas!
La información ofrecida aquí está automatizada mediante acceso diario a los proyectos en GitHub 
y explicación de ChatGPT4.
"""
)
if "nuevo_proyecto" not in st.session_state:
    st.session_state["nuevo_proyecto"] = ''

def get_nuevo_proyecto():
    msg_nuevo_proy = "<span style='color:green'>¡Felicidades! Hemos recogido tu petición y el proyecto se añadirá enseguida.</span>"
    if st.session_state['nuevo_proyecto'] != '':
        try:
            owner, repo = parse_github_url(st.session_state['nuevo_proyecto'])
        except:
            st.write('URL de GitHub inválida. Formato: https://github.com/streamlit/streamlit')
        gh = GitHubRetrieverProjects(owner=owner,repo=repo)
        #get_google_url_img_proyecto(repo)
        proy = Project(
            project_name=repo, project_url=st.session_state['nuevo_proyecto'],
            project_source='github', stars=gh.get_project_stars(), 
            program_language=gh.get_project_language(), author=gh.get_project_author(), 
            description=gh.get_project_description(), inserted_at=datetime.datetime.now(), 
            updated_at=datetime.datetime.now(), activated=False, revised=False
        )
        try:
            db.instert_project(proy)
        except Exception as e:
            if type(e) == IntegrityError:
                msg_nuevo_proy = f"<span style='color:green'>¡El proyecto {repo.upper()} ya había sido pedido recientemente y está ya incluido o pendiente de incluirse! :)</span>"
        st.markdown(msg_nuevo_proy, unsafe_allow_html=True)


nuevo_proyecto = st.text_input(
    "¿No encuentras un módulo? URL del nuevo proyecto a seguir", placeholder="p.ej. https://github.com/sqlalchemy/sqlalchemy",
    key='nuevo_proyecto', on_change=get_nuevo_proyecto()
)


st.write("""
\n
***""")

col1, col2, col3 = st.columns([2, 1, 1])
busqueda = col1.text_input(
    "Búsqueda", placeholder="p.ej. tidyverse, validacion, graficas"
)

select_leguaje = col2.selectbox(
    "Lenguaje", ["Python", "R", TAG_TODOS_LENGUAJES], index=2
)
select_orden = col3.selectbox("Ordenar", ["⭐️ Estrellas", "🐣 Recientes"])

categoria = pills(
    "Categoria",
    [i.name for i in Categorias],
    [i.icon for i in Categorias],
    index=None,
    format_func=lambda x: Categorias.__getitem__(x).value,
    label_visibility="collapsed",
)
st.write("")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


@st.cache_data(ttl=28 * 24 * 3600, show_spinner=False)
def get_projects():
    with Session(db.get_engine()) as session:
        statement = select(ProjectTable)
        if not AUTO_REVIEW_NEW_PROJECT:
            statement = statement.filter_by(activated=True)
        projects = session.exec(statement).fetchall()
    return projects


@st.cache_data(ttl=28 * 24 * 3600, show_spinner=False)
def sort_proyectos(_proyectos: list, by):
    if by == "⭐️ Estrellas":
        return sorted(
            _proyectos,
            key=lambda c: (
                int(c.stars) if c.stars is not None else 0,
                c.image_url is not None,  # items with image first
            ),
            reverse=True,
        )
    elif by == "🐣 Recientes":
        return sorted(
            _proyectos,
            key=lambda c: (
                c.created_at if c.created_at is not None else datetime.datetime(1970, 1, 1),
                c.image_url is not None,  # items with image first
            ),
            reverse=True,
        )
    else:
        raise ValueError("`by` debe ser 'Estrellas' o 'Recientes'")


@st.cache_data(ttl=28 * 24 * 3600, show_spinner=False)
def filter_proyectos(
    _proyectos, language=None, busqueda=None, categoria=None, newer_than=None
):
    if language and language != TAG_TODOS_LENGUAJES:
        _proyectos = list(
            filter(lambda c: language in c.program_language, _proyectos)
        )
    if busqueda:
        _proyectos = list(
            filter(lambda c: busqueda.lower() in c.search_text, _proyectos)
        )
    if categoria:
        _proyectos = list(
            filter(
                lambda c: (categoria in c.category) | (categoria in c.subcategory),
                _proyectos,
            )
        )
    if newer_than:
        _proyectos = list(
            filter(lambda c: c.created_at and c.created_at >= newer_than, _proyectos)
        )
    return _proyectos


def shorten(text, length=100):
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
def show_proyectos(_proyectos, limit=None):
    if limit is not None:
        _proyectos = _proyectos[:limit]

    for i, proyectos_chunk in enumerate(chunks(_proyectos, NUM_COLS)):
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
                else:
                    # TODO: Need to use web URL because we can't expose image through static folder.
                    avatar_path = "https://icon-library.com/images/default-profile-icon/default-profile-icon-16.jpg"
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

                st.write("**Últimas Releases**")
                df = st.session_state["df_releases"]

                exp = True
                for _, e in df[df.repo_url == c.project_url].iterrows():
                    with st.expander(e["name"], expanded=exp):
                        out = format_output_text(e["explanation"])
                        st.text(out)
                        exp = False

                # with st.expander('', expanded=True):
                #    st.dataframe(df[df.repo_url == c.project_url])

                st.write("**Últimas PRs mergeadas**")

                # st.write(" • ".join(formatted_links), unsafe_allow_html=True)
                mdlit(" &nbsp;•&nbsp; ".join(formatted_links))
                # st.caption(", ".join(c.categories))
                st.write("")
                st.write("")
                st.write("")

        # if i < (min(limit, len(components)) // NUM_COLS) - 1:
        # st.write("---")


if "limit" not in st.session_state:
    st.session_state["limit"] = 60

if "df_releases" not in st.session_state:
    st.session_state["df_releases"] = db.run_query(
        f"""
    select *
    from (
    select * , ROW_NUMBER() OVER (PARTITION BY repo_url order by published_at DESC) AS r
    from project_tracker.releases
    ) ord
    where ord.r <= {NUM_HISTORICO}"""
    )

if "df_prs" not in st.session_state:
    st.session_state["df_prs"] = db.run_query(
        f"""
    select *
    from (
    select * , ROW_NUMBER() OVER (PARTITION BY repo_url order by merged_at DESC) AS r
    from project_tracker.prs
    ) ord
    where ord.r <= {NUM_HISTORICO};
    """
    )


def show_more():
    st.session_state["limit"] += 40

proyectos = get_projects()


proyectos = sort_proyectos(proyectos, select_orden)

#if not busqueda and not categoria and select_orden != "🐣 Recientes":
#    "## 🚀 Releases de la última semana"
#    st.write("")
#    new_components = filter_components(
#        components,
#        select_leguaje,
#        busqueda,
#        categoria,
#        newer_than=datetime.now() - timedelta(days=7),
#    )
#    show_components(new_components, limit=4)
#
#    "## 🌟 Favoritos"
#
#st.write("")
#st.write("")

proyectos = filter_proyectos(proyectos, select_leguaje, busqueda, categoria)
show_proyectos(proyectos, st.session_state["limit"])

if len(proyectos) > st.session_state["limit"]:
    st.button("Show more proyectos", on_click=show_more, type="primary")
