import click

from . import __version__


@click.group()
@click.pass_context
@click.version_option(__version__, "--version", "-v", prog_name="ratchet")
def main(ctx: click.Context) -> None:
    click.echo("Hello, world!")
