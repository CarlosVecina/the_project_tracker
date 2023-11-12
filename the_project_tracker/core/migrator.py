from abc import abstractmethod
import pandas as pd

from pydantic import BaseModel

from the_project_tracker.db.pg_conn import PGDataConnection, SettingsSSH
from the_project_tracker.db.sqlite_conn import SQLiteDataConnection


class CodeSpecs(BaseModel):
    # TODO: Read requirements from pyproject/requirements for supporting multi-module check/migration
    module_name: str
    module_version: str | None


class AbstractMigrator(BaseModel):
    specs: CodeSpecs
    connection: PGDataConnection | SQLiteDataConnection = PGDataConnection(
        ssh_config=SettingsSSH()
    )

    @abstractmethod
    def migrate_to_latest(self, **kwargs) -> str:
        raise NotImplementedError("A migrator should migrate to latest ;)")

    def _retrieve_latest_version(self) -> str:
        # Retrieve latests version
        query = f"""select m.tag_name from releases m
            inner join (
                select repo_url, max(inserted_at) as max_date 
                from releases r  
                group by repo_url  
            ) t  on t.repo_url = m.repo_url and t.max_date = m.inserted_at  
            where m.repo_url ilike '%/{self.specs.module_name}'
            """
        last_tag_name = self.connection.run_query(query)
        if len(last_tag_name) > 1:
            raise Exception("Multiple last tag names not allowed: ", last_tag_name)
        return last_tag_name

    def _retrieve_release_notes(self, reference_version: str) -> pd.DataFrame:
        query = f"""
            select tag_name, explanation 
            from releases r 
            where r.repo_url ilike '%/{self.specs.module_name}';
        """
        return self.connection.run_query(query)

    # @abstractmethod
    # def migrate_to_version(self, version=str, **kwargs) -> str:
    #    raise NotImplementedError("A migrator should migrate to given version ;)")


class OpenAIMigrator(AbstractMigrator):
    def migrate_to_latest(self, code_file: str, **kwargs) -> str:
        last_tag_name = self._retrieve_latest_version()

        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "python_file"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a expert Python code migrator .",
                },
                {"role": "user", "content": "Who won the world series in 2020?"},
            ],
        )

        # Set ot infhere the current code version
        # self.specs.module_version | self._infere_current_version
