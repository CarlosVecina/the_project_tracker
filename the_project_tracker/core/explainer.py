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
    max_len_input: int = 1500
    max_len_output: int = 1500

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
        content = f"""Explain the following {entity} in the '{repo}' project without access the current repository.\n
        Avoid talking about reviewer or interestad users. {entity} title: {title}. Focus on the information relevant for a code migration perspective, 
        like function and methods deprecations and renames, performance improvements, enhancement. Do it in a precise way as it was the prompt to reconstruct the change version."""
        if body:
            content += f"Description: {body[:self.max_len_input]}."
        if code_diffs:
            content += f"Code diffs: {code_diffs[:(max(0, self.max_len_input - len(content)))]}"
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "model": "gpt-3.5-turbo",
            "max_tokens": self.max_len_output,
            "temperature": 0.7,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        if "error" in result:
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
        content = f"""Resume y traduce al español la siguiente {entity} en el proyecto '{repo}' sin necesidad de acceder al repositorio de github. Centrate en la información relevante desde una perspectiva de migración de versiones de código.
        Como por ejemplo deprecación de funciones, renombrado, mejoras de rendimiento y nuevas funciones. Hazlo tal y como tú lo necesitarías para hacer una recostrucción y migración entre versiones de código.\n
        Evita hablar sobre los revisores. {entity} titulo:  {title}"""
        if body:
            content += f"La descripcion en Ingles es: {body[:self.max_len_input]}."
        if code_diffs:
            content += f"Las diferencias de codigo: {code_diffs[:(max(0, self.max_len_input - len(content)))]}"
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "model": "gpt-3.5-turbo",
            "max_tokens": self.max_len_output,
            "temperature": 0.7,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        if "error" in result:
            raise Exception("OpenAI request error:", result["error"])
        return result["choices"][0]["message"]["content"].strip()
