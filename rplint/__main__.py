import click

import rplint.checks as _checks

__version__ = "0.8.0"


@click.command("rplint")
@click.option(
    "-l",
    "--line-length",
    type=click.INT,
    default=500,
    help="Line length to check for [500].",
)
@click.argument(
    "input_file",
    type=click.File(mode="r"),
    required=True,
)
@click.version_option(version=__version__)
def rplint(input_file, line_length):
    """Checks a Markdown file for common writing issues.

    INPUT_FILE The Markdown file to check.
    """
    checks = {
        name: check()
        for name, check in _checks.__dict__.items()
        if name.endswith("Check")
    }
    checks["LineLengthCheck"].line_length = line_length
    lines = input_file.readlines()
    for check in checks.values():
        check.run(lines)
        if check:
            click.secho(check, fg="red")
        else:
            click.secho(f"{check}... Passes!", fg="green")
