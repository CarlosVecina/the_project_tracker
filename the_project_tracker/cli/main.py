import click

from the_project_tracker.core.pipeline import PullRequestPipeline, ReleasePipeline
from the_project_tracker.core.stargazers import (
    DiscoveryTopProjectEvolutionPipeline,
    ProjectEvolutionPipeline,
)


@click.group()
@click.option(
    "-u", "--url", help="Github project url", default=None, show_default=True
)  # prompt="Github project url"
@click.pass_context
def pipeline_cli(ctx, url: str):
    ctx.ensure_object(dict)
    ctx.obj["url"] = url
    print(f"URL param set to: {ctx.obj['url']}")


@click.command("releases")
@click.option(
    "-n",
    "--max_releases_num",
    prompt="Max release number to track",
    help="Max release number to track",
)
@click.pass_context
def releases(ctx, max_releases_num: int):
    pipeline = ReleasePipeline(
        repo_url=ctx.obj["url"], max_releases_num=max_releases_num
    )
    pipeline.run()


@click.command("prs")
@click.option(
    "-n",
    "--max_pr_num",
    prompt="Max merged PRs number to track",
    help="Max merged PRs number to track",
)
@click.option("-cd", "--code_diff", is_flag=True, default=False)
@click.option("-f", "--fail", help="Fail if new repo", is_flag=True, default=False)
@click.pass_context
def prs(ctx, max_pr_num: int, code_diff: bool, fail: bool):
    pipeline = PullRequestPipeline(
        repo_url=ctx.obj["url"], max_pr_num=max_pr_num, include_code_diffs=code_diff
    )
    pipeline.run(fail_if_new=fail)


@click.command("discover_proyects_evolution")
def discover_proyect_evolution():
    pipeline = DiscoveryTopProjectEvolutionPipeline()
    pipeline.run()


@click.command("project_evolution")
def project_evolution():
    pipeline = ProjectEvolutionPipeline()
    pipeline.run()


pipeline_cli.add_command(prs, "prs")
pipeline_cli.add_command(releases, "releases")
pipeline_cli.add_command(project_evolution, "project_evolution")
pipeline_cli.add_command(discover_proyect_evolution, "discover_proyect_evolution")

if __name__ == "__main__":
    pipeline_cli(obj={})
