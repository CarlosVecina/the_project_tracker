from typing import Dict, Optional

import sqlalchemy as db

DDL_PRS = """
            CREATE TABLE IF NOT EXISTS prs (
                repo_url TEXT NOT NULL,
            	pr_id INTEGER NOT NULL,
                inc_code_diffs INTEGER NOT NULL,
                merged_at TEXT,
                inserted_at TEXT,
                updated_at TEXT,
    	        pr_title TEXT NOT NULL,
    	        pr_body TEXT,
    	        commits_url TEXT NOT NULL,
                explanation TEXT NOT NULL,
                PRIMARY KEY (repo_url, pr_id, inc_code_diffs)
            );
            """

DDL_RELEASES = """
            CREATE TABLE IF NOT EXISTS releases (
                repo_url TEXT NOT NULL,
                name TEXT NOT NULL,
                tag_name TEXT NOT NULL,
                published_at TEXT NOT NULL,
                assets TEXT,
                body TEXT NOT NULL,
                explanation TEXT NOT NULL,
                inserted_at TEXT,
                updated_at TEXT,
                PRIMARY KEY (repo_url, tag_name)
            );
        """
DDL_PROJECTS = """
            CREATE TABLE IF NOT EXISTS projects (
            	project_name varchar NOT NULL,
            	project_url varchar NOT NULL,
            	project_source varchar NOT NULL,
            	stars varchar NULL,
            	description varchar NULL,
            	created_at timestamp NULL,
            	inserted_at timestamp NOT NULL,
            	updated_at timestamp NOT NULL,
            	image_url varchar NULL,
            	search_text varchar NULL,
            	author varchar NULL,
            	program_language varchar NULL,
            	category varchar NULL,
            	subcategory varchar NULL,
            	docs_url varchar NULL,
            	top_contributors varchar NULL,
            	author_avatar_url varchar NULL,
            	last_release varchar NULL,
            	last_release_at varchar NULL,
            	release_notes varchar NULL,
            	activated bool NULL DEFAULT false,
            	revised bool NULL DEFAULT false,
            	CONSTRAINT projects_pk PRIMARY KEY (project_name, project_url)
            );
"""
def create_upsert_method(
    meta: db.MetaData, extra_update_fields: Optional[Dict[str, str]]
):
    """
    Create upsert method that satisfied the pandas's to_sql API.
    """

    def method(table, conn, keys, data_iter):
        sql_table = db.Table(table.name, meta, autoload=True)

        # list of dictionaries {col_name: value} of data to insert
        values_to_insert = [dict(zip(keys, data)) for data in data_iter]

        # create insert statement using postgresql dialect.
        insert_stmt = db.dialects.postgresql.insert(sql_table, values_to_insert)

        update_stmt = {exc_k.key: exc_k for exc_k in insert_stmt.excluded}
        if extra_update_fields:
            update_stmt.update(extra_update_fields)

        # index elements are primary keys of a table
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=sql_table.primary_key.columns, set_=update_stmt
        )

        conn.execute(upsert_stmt)

    return method
