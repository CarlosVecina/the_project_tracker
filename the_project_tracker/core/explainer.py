import json
from abc import abstractmethod

import requests
from pydantic import BaseSettings


class AbstractExplainer(BaseSettings):
    @abstractmethod
    def explain(self, **kwargs) -> str:
        raise NotImplementedError("An explainer should explain ;)")


class DummyExplainer(AbstractExplainer):
    def explain(self, **kwargs):
        return "Dummy"


class OpenAIExplainer(AbstractExplainer):
    class Config:
        title = "OpenAI Explainer"
        env_prefix = "OPENAI_"
        case_sensitive = False
        underscore_attrs_are_private = True

    token: str

    def explain(self, **kwargs) -> str:
        return self._get_gpt35_turbo_explanation(**kwargs)

    def explain_es(self, **kwargs) -> str:
        return self._get_gpt35_turbo_explanation_esp(**kwargs)

    # TODO: Create a PR / PRExplained entity and accept PR formated in this function
    def _get_gpt35_turbo_explanation(
        self,
        repo: str,
        title: str,
        body: str,
        entity: str = "pull request",
        code_diffs: str = None,
        **kwargs,
    ) -> str:
        # url = 'https://api.openai.com/v1/engines/davinci-codex/completions'
        # url = 'https://api.openai.com/v1/completions'
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        content = f"""Explain the following {entity} in the '{repo}'  project without access the current repository.\n
        Avoid talking about reviewer or interestad users. {entity} title: {title}"""
        if body:
            content += f"Description: {body[0:400]}."
        if code_diffs:
            content += f"Code diffs: {code_diffs[0:1500]}"
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "model": "gpt-3.5-turbo",
            "max_tokens": 300,
            "temperature": 0.7,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        if 'error' in result:
            raise Exception("OpenAI request error:", result["error"])
        return result["choices"][0]["message"]["content"].strip()

    def _get_gpt35_turbo_explanation_esp(
        self,
        repo: str,
        title: str,
        body: str,
        entity: str = "pull request",
        code_diffs: str = None,
        **kwargs,
    ) -> str:
        # url = 'https://api.openai.com/v1/engines/davinci-codex/completions'
        # url = 'https://api.openai.com/v1/completions'
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        content = f"""Resume la siguiente {entity} en el proyecto '{repo}' sin necesidad de acceder al repositorio de github.\n
        Evita hablar sobre los revisores. {entity} titulo:  {title}"""
        if body:
            content += f"La descripcion es: {body[0:400]}."
        if code_diffs:
            content += f"Las diferencias de codigo: {code_diffs[0:1500]}"
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "model": "gpt-3.5-turbo",
            "max_tokens": 300,
            "temperature": 0.7,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        if 'error' in result:
            raise Exception("OpenAI request error:", result["error"])
        return result["choices"][0]["message"]["content"].strip()
