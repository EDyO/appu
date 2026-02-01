import sys
from cli import get_logger, parse_config
from audio import (
    load_mp3,
    get_jingles,
    glue_tracks,
    normalize_audio,
    clamp_silence,
    add_tail_silence,
)
from publish import upload_file

logger = get_logger()
cfg = parse_config()

# Read mp3 tags from config file
mp3_tags = {
    'title': cfg['title'],
    'artist': cfg['artist'],
    'album': cfg['album'],
    'track': cfg['track'],
    'comment': cfg['comment'],
}

logger.info("Importing podcast")
podcast = load_mp3(cfg['podcast_file'], "podcast")

logger.info("Clamping long silences")
podcast = clamp_silence(podcast)

logger.info("Generating jingles")
opening, ending = get_jingles(cfg['song_file'])

logger.info("Normalizing podcast audio")
podcast = normalize_audio(podcast)

logger.info("Generating final podcast file: opening + podcast + ending")
final = glue_tracks([
    (opening, 0),
    (podcast, 800),  # fade un poco más largo para una entrada más suave
    (ending, 500),   # fade-in/out suave del outro sin comerse el final
])

logger.info("Adding tail silence")
final = add_tail_silence(final)

logger.info("Exporting final file")
final.export(
    cfg['final_file'],
    format="mp3",
    tags=mp3_tags,
    bitrate='48000',
    parameters=["-ac", "1"],
    id3v2_version='3',
    cover=cfg['cover_file'],
)

logger.info("Done! File {} generated correctly".format(cfg['final_file']))

# Skip upload when user requests no-upload or when podcast_bucket is empty
if "--no-upload" in sys.argv or not cfg.get('podcast_bucket'):
    logger.info("Skipping upload (no-upload flag or empty podcast_bucket).")
else:
    if upload_file(cfg['final_file'], cfg['podcast_bucket']):
        logger.info("Episode uploaded to {}".format(cfg['podcast_bucket']))
