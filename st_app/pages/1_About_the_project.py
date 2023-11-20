import streamlit as st

st.set_page_config(page_title="Sobre OSPT", page_icon="📈")

st.write("")

st.markdown(
    """

## About the Project

This project facilitates the automated tracking of your favorite Open Source projects. Stay up to date with all the changes at a glance, whether you're an individual contributor without having to visit every Release note or in a management role where you want to keep track of the changes happening in the most used projects of your team.

Underneath, through a Retriever of the projects and an Explainer (using LLMs, currently OpenAI ChatGPT 3.5), information about Releases and PRs is compiled and summarized. This includes title, body, code differences, release notes, and changelog.

For the inclusion of new projects, the application offers an input field where users can suggest new projects to monitor. After validation of the input, it is inserted into the database and pending validation. Once validated, the information will be collected and monitored daily. A 'next step' would be to perform all validations 'on the fly' and leave the inclusion of projects 100% automated.
""")

st.write("")

st.markdown("""
            
##  Object Structure and Data Model
In this repository, we can find two modules:

-  `the_project_tracker`, the data retrieval and summary module by an LLM
-  `st_app`, the module containing the Streamlit application.
            
The fundamental elements of this project are:

- `Pipeline`: It is the main program, responsible for executing the entire process from collecting data from Github, parsing it, summarizing through AI, and inserting into a database.
- `Retriever`: Responsible for gathering information on Projects, Releases, and PRs. Currently, GitHubRetriever has been implemented, which is in charge of collecting this data through the GitHub API.
- `Explainer`: Responsible for calling the NLP model capable of summarizing content. Currently, OpenAIExplainer has been implemented, which is responsible for making calls to the OpenAI API so that ChatGPT3.5 can summarize and translate entities. It uses titles, bodies, and code differences from Releases and PRs.
- `DataConnection`: In charge of retrieving data and inserting it into a database. Mainly, PGDataConnection is used, although for educational/debugging purposes, SQLiteDataConnection has also been implemented.
- `App de Streamlit`: A separate module responsible for providing an App where data is made available in a user-friendly manner.
            
The entities they work with, and which are generally known, are:
- `Project`
- `Release`
- `PR`
These are [SQLModel](https://sqlmodel.tiangolo.com/) models (from the creator of FastAPI), which combine the power of Pydantic with SQLAlchemy.
"""
)

