#!/bin/sh

# DB creation
.venv/bin/python3 the_project_tracker/db/sqlite_conn.py

# Streamlit service
.venv/bin/python3 -m streamlit run st_app/Proyectos.py $APP_PORT