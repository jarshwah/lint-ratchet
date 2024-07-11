import dataclasses
import pathlib
from typing import cast

import click

from . import __version__, configuration, usecases


@dataclasses.dataclass
class MainOptions:
    config: configuration.Config
    root: pathlib.Path
    check_dir: pathlib.Path


@click.group()
@click.pass_context
@click.version_option(__version__, "--version", "-v", prog_name="ratchet")
@click.option(
    "--root",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    default=".",
    help="The path to the root of the project to check, where the pyproject.toml file is located. Defaults to the current directory.",
)
def main(ctx: click.Context, root: pathlib.Path) -> None:
    try:
        config = configuration.open_configuration(root)
    except (
        configuration.ProjectFileNotFoundError,
        configuration.RatchetNotConfiguredError,
        configuration.RatchetMisconfiguredError,
    ) as e:
        raise click.ClickException(str(e)) from e

    check_dir = root / config.path
    if not check_dir.exists():
        raise click.ClickException(f"Path {check_dir} does not exist")

    ctx.obj = MainOptions(config, root, check_dir)


@main.command()
@click.pass_context
def check(ctx: click.Context) -> None:
    main_options = cast(MainOptions, ctx.obj)
    failures = 0
    rule_num = len(main_options.config.rules)
    for result in usecases.check(main_options.check_dir, main_options.config):
        if result.failure:
            failures += 1
            click.secho(
                f"{result.rule.tool.value}.{result.rule.code} failed: {result.new_count} > {result.rule.violation_count}",
                fg="red",
            )
    if failures:
        raise click.ClickException(click.style(f"❌ {failures}/{rule_num} failed", fg="red"))
    click.secho("✅ All rules passed", fg="green", err=True)
