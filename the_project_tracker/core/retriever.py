import requests
from pydantic import BaseSettings


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

    def get_last_release(self, max_releases_num: int) -> str:
        headers = {"Authorization": f"token {self.token}"}
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            releases = response.json()
            output = list()
            for release in releases:
                if len(output) < max_releases_num:
                    output.append(
                        {
                            "name": release["name"],
                            "tag_name": release["tag_name"],
                            "published_at": release["published_at"],
                            "assets": str(release["assets"]),
                            "body": str(release["body"]),
                        }
                    )
            return output
        else:
            print(f"Failed to retrieve release data: {response.status_code}")


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
