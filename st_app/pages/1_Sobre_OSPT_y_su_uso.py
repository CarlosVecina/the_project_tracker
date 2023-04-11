import streamlit as st

st.set_page_config(page_title="Sobre OSPT", page_icon="📈")

# st.write("# Welcome to Streamlit! 👋")

# st.sidebar.success("Select a demo above.")

st.markdown(
    """
## Sobre el proyecto y Concurso Streamlit

Este proyecto consiste en permitir el **seguimiento de tus proyectos Open Source favoritos de manera automatizada**. Mediante un `Retriever` de los proyectos y un `Explainer` (usando LLMs, actualmente OpenAI ChatGPT 3.5) se recopila la información sobre `Releases` y `PRs`, y se resume. Teniendo en cuenta título, cuerpo, diferencias de código, notas de versión y *changelog*.

**Se desarrolla la aplicacion en Streamlit y en Español, para presentarla al [concurso de Streamlit](https://discuss.streamlit.io/t/anunciando-el-concurso-de-streamlit-en-espanol/40274)**

Para la inclusión de nuevos proyectos, la aplicación ofrece un campo de entrada donde los usuarios pueden sugerir nuevos proyectos a monitorizar. Después de una validación del *input*, se inserta en BBDD y queda pendiente de validar. Una vez validado, se recopilará la información y monitorizará diariamente. Un 'siguiente paso' sería realizar todas las validaciones 'al vuelo' y dejar la inclusión de proyectos 100% autmatizada.

<br>

## Estructura de Objetos y Modelo de Datos

En este repositorio podemos encontrar dos módulos:
-  `the_project_tracker`, el módulo de obtención de datos y resumen por parte de un LLM
-  `st_app`, el módulo que contiene aplicación de Streamlit.

Los elementos fundamentales de este proyecto son:
- `Pipeline`: Es el programa principal, encargado de ejecutar de principio a fin la recogida de datos desde Github, parseo de los mismos, resumen a través de IA, e inserción en base de datos.
- `Retriever`: Es el responsabe de recabar la información sobre los Proyectos, Releases y PRs. Actualmente se ha implementado el GitHubRetriever, que es el encargado de recoger estos datos mediante la API de GitHub.
- `Explainer`: Es el responsable de llamar al modelo de NLP capaz de resumir el contenido. Actualmente se ha implementado el OpenAIExplainer, que es el encargado de hacer las llamadas a la API de OpenAI para que ChatGPT3.5 resuma y traduzca las entidades. Utiliza tanto títulos, como cuerpos como diferencias de código de las Releases y PRs.
- `DataConnection`: Es la encargada de recuperar datos e insertar en base de datos. Principalmente se utiliza la PGDataConnection, aunque para propositos educativos/debug, también se ha implementado SQLiteDataConnection.
- `App de Streamlit`: Es un módulo aparte y se encarga de ofrecer una App donde se disponibilizan los datos de una manera *user-friendly*.

Las entidades con las que trabajan, y que son generalemente conocidas, son:
- `Proyecto`
- `Release`
- `PR`

Son modelos de [SQLModel](https://sqlmodel.tiangolo.com/) (del creador de FastApi), que auna el poder de Pydantic con el de SQLAlchemy.
"""
)
