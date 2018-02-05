from pydub import AudioSegment
from pydub.silence import split_on_silence
import ConfigParser
import logging
import sys

def parse_args():
    """Debug mode with param -debug"""
    if "-debug" in sys.argv :
        l.setLevel(logging.DEBUG)

def parse_config():
    """Read config file and loads parameters as variables"""
    configParser = ConfigParser.RawConfigParser()
    configFilePath = r'./config.cfg'
    configParser.read(configFilePath)
    for section in configParser.sections():
        for name, value in configParser.items(section):
            globals()[name] = value

def load_mp3(mp3_file_name):
    """
    This tries to load the audio from a named mp3 file.
    It checks the filename has mp3 extension.
    """
    if mp3_file_name.lower().endswith('.mp3'):
        audio = AudioSegment.from_mp3(mp3_file_name)
    else:
        sys.exit('Incorrect audio file format. The file must have .mp3 extension')
    return audio

def get_jingles(song_file_name):
    """
    This function returns both starting and ending
    jingles.
    """
    song = load_mp3(song_file_name)
    return song[:20000], song[40000:]

def glue_tracks(tracks):
    """
    This functions glues all tracks in a single one,
    using the specified fade for each track, and
    returns the resulting audio.
    """
    final = tracks[0][0]
    for audio, fade in tracks[1:]:
        final = final.append(audio, crossfade=fade)
    return final

# Using logger instead of print
l = logging.getLogger("pydub.converter")
l.addHandler(logging.StreamHandler())

parse_args()
parse_config()

# Read mp3 tags from config file
mp3_tags={
    'title': title,
    'artist': artist,
    'album': album,
    'track': track,
    'comment': comment,
}

l.info("Importing podcast")
podcast = load_mp3(podcast_file)

l.info("Generating jingles")
opening, ending = get_jingles(song_file)

#podcast = split_on_silence(podcast) <-- TODO

l.info("Normalizing podcast audio")

podcast = podcast.normalize()

l.info("Generating final podcast file: opening + podcast + ending")

final = glue_tracks([(opening, 0), (podcast, 1000), (ending, 4000)])

l.info("Exporting final file")

final.export(final_file, format="mp3", tags=mp3_tags, bitrate='48000', parameters=["-ac", "1"], id3v2_version='3', cover=cover_file)

l.info("Done! File {} generated correctly".format(final_file))
