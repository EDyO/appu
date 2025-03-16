import typer
from loguru import logger

from appu2.logging import LogLevel, setup_logging

from .audio import concat, normalize, split
from .config import ROOT_PROJECT_PATH, settings
from .episode import load_episode
from .remote import download, upload


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


@app.command(name="appu", help="Old appu command")
def app_appu(episode_yaml) -> None:
    logger.info(f"Loading episode {episode_yaml} config")
    episode = load_episode(episode_yaml)

    master_recording = download(episode.master)
    intro_song = download(episode.intro)
    cover_file = download(episode.cover)

    logger.info("Normalizing master audio")
    master_audio = normalize(master_recording)

    logger.info("Extract intro and outro")
    intro_audio, outro_audio = split(intro_song, slice(0, 20000, None), slice( -40000, None, None))

    logger.info("Concatenating intro, master audio, and outro")
    final_audio = concat([(intro_audio, 0), (master_audio, 1000), (outro_audio, 4000)])

    logger.info("Exporting track")
    final_audio.export(
        episode.filename,
        format="mp3",
        tags=episode.tags,
        bitrate="48000",
        parameters=["-ac", "1"],
        id3v2_version="3",
        cover=cover_file,
    )

    upload(episode.filename, episode.destination)
