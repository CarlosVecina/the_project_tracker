create_local_db:
	poetry run python the_project_tracker/db/sqlite_conn.py
install:
	poetry install
precommit:
	poetry run pre-commit run --all-files
run_app:
	poetry install -E st_app
	poetry run streamlit run st_app/Proyectos.py
track_prs:
	poetry run sh src/run_pipeline_prs.sh
track_releases:
	poetry run sh src/run_pipeline_releases.sh
