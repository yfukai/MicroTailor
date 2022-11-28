"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """microtailor."""


if __name__ == "__main__":
    main(prog_name="MicroTailor")  # pragma: no cover
