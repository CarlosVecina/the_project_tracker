# OSPT - Seguimiento de proyectos Open Source

## Proyecto y Concurso Streamlit

Este proyecto consiste en permitir el **seguimiento de tus proyectos Open Source favoritos de manera automatizada**. Mediante un `Retriever` de los proyectos y un `Explainer` (usando LLMs, actualmente OpenAI ChatGPT 3.5) se recopila la información sobre `Releases` y `PRs`, y se resume. Teniendo en cuenta título, cuerpo, diferencias de código, notas de versión y *changelog*.

Esta aplicación se encuentra desplegada en el Cloud de Streamlit:

---- 
[Acceso al proyecto desplegado en Streamlit Cloud](https://carlosvecina-the-project-tracker-st-appproyectos-mv7k8w.streamlit.app/)

---- 

con su correspondiente base de datos donde se recopila información varias veces al día.

**Se desarrolla la aplicacion en Streamlit y en Español, para presentarla al [concurso de Streamlit](https://discuss.streamlit.io/t/anunciando-el-concurso-de-streamlit-en-espanol/40274)**

<p align="center">
  <img src="https://global.discourse-cdn.com/business7/uploads/streamlit/optimized/3X/1/4/14ff1b75e72ff93755287ef61217f72c746a20da_2_1000x1000.jpeg" width="250" title="Streamlit Concurso en Españil">
</p>

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

<p align="center">
  <img src="./docs/data_models.drawio.png" width="400" title="Streamlit Concurso en Españil">
</p>


Los hemos creado como modelos de [SQLModel](https://sqlmodel.tiangolo.com/) (del creador de FastApi), que auna el poder de Pydantic con el de SQLAlchemy.

<br>

## Como ejecutar

Este proyecto utiliza [Poetry](https://python-poetry.org/docs/) como gestor de dependencias. Asegurate de tenerlo instalado. En caso contrario, puedes ejecutar:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Esta aplicación requiere de las siguientes variables de entorno:
```bash
# Necesarios: para el GH Retriever y el OpenAI Explainer
GITHUB_TOKEN
OPENAI_TOKEN

# Para la BBDD tenemos dos opciones
# 1: Nombre si se pretende usar la bbdd local SQLite
LOCAL_DB

# 2: RECOMENDADO Si se pretende usar un PG desplegado
PG_HOST
PG_PORT
PG_DATABASE
PG_USERNAME
PG_PWD
```

Realmente, por el momento, es posible que no quieras ejecutar este proyecto en local sino consumirlo desde la app de Streamlit. Publicar este repositorio queda más a propósitos didácticos. Esto es debido a que tanto la aplicación de Streamlit como la base de datos está desplegada y es accesible por los usuarios. 

Para ejecutar el track de Releases y de PRs:
```bash
make track_releases
make track_prs
```

Estos comandos ejecutarán los scripts localizados en `src/`.

El programa de trackeo de Projectos está preparado para funcionar con una Postgres. La aplicación de Streamlit está parametrizada para aceptar tanto esto, como un SQLite en local, aunque todo el desarrollo se ha hecho con un PG desplegado, configurando las credenciales en variables de entorno como se ha explicado unas lineas arriba.

Si se quisiese ejecutar con base de datos local, estos serían los pasos:

```bash
make run_app_local_db
```
Para popular las tablas, se deberá hacer alguna modificación, de momento, para usar la SQLiteDataConnection. En cuestión de días se parametrizará este comportamiento para poder lanzar el tracker de Releases y PRs con base de datos en local.

<br>

<br>

Agradecimientos a la inspiración en el diseño de la página principal a https://github.com/jrieke/components-hub, proyecto en el cual estaré más que encantado en proponer/sugerir algunas mejoras que bajo mi punto de vista se han implementado en este.
