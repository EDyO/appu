import typer

from appu2.logging import LogLevel, setup_logging

from .config import ROOT_PROJECT_PATH, settings

app = typer.Typer(help="appu CLI", no_args_is_help=True)


LOG_LEVEL_OPTION = typer.Option(
    LogLevel.INFO,
    "--log-level",
    "-l",
    case_sensitive=False,
    help="Set the logging level",
)


@app.callback()
def callback(log_level: LogLevel | None = LOG_LEVEL_OPTION) -> None:
    """Initialize logging and other global settings."""
    setup_logging(level=log_level)


@app.command(name="test", help="Test Command")
def app_test() -> None:
    print(settings.debug)
    print("Hello World!")
    print(ROOT_PROJECT_PATH)
