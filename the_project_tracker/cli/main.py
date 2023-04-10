import click

from the_project_tracker.core.pipeline import PullRequestPipeline, ReleasePipeline


@click.group()
@click.option("-u", "--url", prompt="Github project url", help="Github project url")
@click.pass_context
def pipeline_cli(ctx, url: str):
    ctx.ensure_object(dict)
    ctx.obj["url"] = url
    print(ctx.obj["url"])


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


@click.command()
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


pipeline_cli.add_command(prs, "prs")
pipeline_cli.add_command(releases, "releases")

if __name__ == "__main__":
    pipeline_cli(obj={})
