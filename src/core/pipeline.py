import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DAVINCI_API_KEY = os.getenv("DAVINCI_API_KEY")
MAX_PRS = 2


def get_last_merged_pr_info(owner, repo):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed&sort=updated&direction=desc"

    response = requests.get(url, headers=headers)
    prs = response.json()
    for pr in prs:
        if pr["merged_at"] is not None:
            breakpoint()
            return pr["title"], pr["body"], pr["commits_url"], pr["number"]

    return None, None, None, None


def get_code_diffs(repo_url, pr_number):
    owner, repo = repo_url.split("/")[-2:]
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"

    response = requests.get(url, headers=headers)
    files = response.json()
    diffs = []

    for file in files:
        if file["status"] != "removed":
            diffs.append(f'File: {file["filename"]}\nPatch:\n{file["patch"]}')

    return "\n".join(diffs)


def get_gpt35_turbo_explanation(repo, pr_title, pr_body, code_diffs):
    # url = 'https://api.openai.com/v1/engines/davinci-codex/completions'
    # url = 'https://api.openai.com/v1/completions'
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DAVINCI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        #'prompt': f'Explain the following pull request in simple terms:\nTitle: {pr_title}\nDescription: {pr_body}',#\nCode diffs:\n{code_diffs[0:500]}',
        "messages": [
            {
                "role": "user",
                "content": f"Explain the following pull request in the {repo} repository:\nTitle: {pr_title}\nDescription: {pr_body[0:200]} . Avoid talking about reviewer or interestad users.",
            }
        ],
        "model": "gpt-3.5-turbo",
        "max_tokens": 250,
        "temperature": 0.7,
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


def main():
    repo_url = input("Enter the GitHub repo URL: ")
    owner, repo = repo_url.split("/")[-2:]
    pr_title, pr_body, commits_url, pr_number = get_last_merged_pr_info(owner, repo)
    if pr_title and pr_body:
        code_diffs = get_code_diffs(repo_url, pr_number)
        explanation = get_gpt35_turbo_explanation(repo, pr_title, pr_body, code_diffs)
        print("\nPR(s):\n", explanation)
        print("\nPR Explanation:\n", explanation)
    else:
        print("No merged PRs found in the repository.")


if __name__ == "__main__":
    main()
