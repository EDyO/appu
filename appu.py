from cli import get_logger, parse_config
from audio import load_mp3, get_jingles, glue_tracks

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

logger.warning("Importing podcast")
podcast = load_mp3(cfg['podcast_file'],"podcast")

logger.warning("Generating jingles")
opening, ending = get_jingles(cfg['song_file'])

logger.warning("Normalizing podcast audio")
podcast = podcast.normalize()

logger.warning("Generating final podcast file: opening + podcast + ending")
final = glue_tracks([(opening, 0), (podcast, 1000), (ending, 4000)])

logger.warning("Exporting final file")
final.export(
    cfg['final_file'],
    format="mp3",
    tags=mp3_tags,
    bitrate='48000',
    parameters=["-ac", "1"],
    id3v2_version='3',
    cover=cfg['cover_file'],
)

logger.warning("Done! File {} generated correctly".format(cfg['final_file']))
