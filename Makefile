create_local_db:
	poetry run python the_project_tracker/db/sqlite_conn.py
export_requeriments:
	poetry build
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	ex -sc '1i|./dist/the_project_tracker-0.1.0-py3-none-any.whl' -cx requirements.txt
install:
	poetry install
precommit:
	poetry run pre-commit run --all-files
run_app:
	poetry install #-E st_app
	poetry run streamlit run st_app/Proyectos.py
run_app_local_db:
	poetry install #-E st_app
	poetry run python the_project_tracker/db/sqlite_conn.py
	LOCAL_DB=tracker_db.sqlite poetry run streamlit run st_app/Proyectos.py
track_prs:
	poetry run sh src/run_pipeline_prs.sh
track_releases:
	poetry run sh src/run_pipeline_releases.sh
