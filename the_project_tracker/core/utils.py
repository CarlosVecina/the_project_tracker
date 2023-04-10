def parse_github_url(github_url: str) -> tuple[str]:
    owner, repo = github_url.strip("/").split("/")[-2:]
    return (owner, repo)
