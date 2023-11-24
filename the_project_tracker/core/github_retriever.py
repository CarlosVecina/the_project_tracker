import requests
from pydantic import BaseSettings
import re


class AbstractRetriever(BaseSettings):
    # TODO: Interface to be defined
    pass


class GitHubRetriever(AbstractRetriever):
    class Config:
        title = "GitHub Retriever"
        env_prefix = "GITHUB_"
        case_sensitive = False
        underscore_attrs_are_private = True

    token: str


class GitHubRetrieverProjects(GitHubRetriever):
    class Config:
        title = "GitHub Retrieve Project info"
        env_prefix = "GITHUB_"
        case_sensitive = False
        underscore_attrs_are_private = True

    owner: str
    repo: str

    _response = None

    def _request(self) -> None:
        headers = {"Authorization": f"token {self.token}"}
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self._response = response.json()
        else:
            raise Exception("An error occurred: {response.status_code}")

    def get_response(self) -> str:
        if not self._response:
            self._request()
        return self._response

    def get_project_stars(self) -> str:
        if not self._response:
            self._request()
        return self._response["stargazers_count"]

    def get_project_language(self) -> str:
        if not self._response:
            self._request()
        return self._response["language"]

    def get_project_description(self) -> str:
        if not self._response:
            self._request()
        return self._response["description"]

    def get_project_author(self) -> str:
        if not self._response:
            self._request()
        return self._response["owner"]["login"]


class GitHubRetrieverReleases(GitHubRetriever):
    owner: str
    repo: str

    # Hard assumption about importance citation precedence
    recursive_release_exploration: int = 0

    def get_last_release(self, max_releases_num: int) -> str:
        headers = {"Authorization": f"token {self.token}"}
        n_pages = max_releases_num // 100 + 1
        output = list()
        for page in range(1, n_pages):
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases?per_page={min(100, max_releases_num)}&page={page}"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                releases = response.json()
                for release in releases:
                    output.append(
                        {
                            "name": release["name"],
                            "tag_name": release["tag_name"],
                            "published_at": release["published_at"],
                            "assets": str(release["assets"]),
                            "body": str(release["body"]),
                        }
                    )
            else:
                print(f"Failed to retrieve release data: {response.status_code}")
        return output
    
    def expand_body_cited_prs(self, body: str) -> str:
        pr_number_regex = r"#(\d+)"
        pr_numbers = re.findall(pr_number_regex, body)
        for pr_n in pr_numbers[:self.recursive_release_exploration]:
            url = f'https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_n}'
            response = requests.get(url, headers={"Authorization": f"token {self.token}", "X-GitHub-Api-Version": "2022-11-28", "Accept": "application/vnd.github+json"}).json()
            body = body.replace(f'#{pr_n}', f'Title and body: {response.get("title", "")} {response.get("description", "")}')
        return body


class GitHubRetrieverPRs(GitHubRetriever):
    owner: str
    repo: str

    def retrieve(self, max_pr_num: int) -> list | None:
        return self.get_last_n_merged_prs_info(max_pr_num)

    def get_last_n_merged_prs_info(self, max_pr_num: int) -> list | None:
        headers = {"Authorization": f"token {self.token}"}
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls?state=closed&sort=updated&direction=desc&per_page=50&page=1"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            prs = response.json()
            output = list()
            for pr in prs:
                if (pr["merged_at"] is not None) & (len(output) < max_pr_num):
                    output.append(
                        {
                            "title": pr["title"],
                            "body": pr["body"],
                            "commits_url": pr["commits_url"],
                            "number": pr["number"],
                            "merged_at": pr["merged_at"],
                        }
                    )
            return output

    def get_code_diffs(self, pr_number: int) -> str:
        headers = {"Authorization": f"token {self.token}"}
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}/files"

        response = requests.get(url, headers=headers)
        files = response.json()
        diffs = []
        for file in files:
            if (file["status"] != "removed") & (hasattr(files, "patch")):
                diffs.append(f'File: {file["filename"]}\nPatch:\n{file["patch"]}')

        return "\n".join(diffs)

class SphinxDocumentationRetriever(AbstractRetriever):
    url: str
    
    def retrieve(self, max_pr_num: int) -> list | None:
        return self.get_last_n_merged_prs_info(max_pr_num)