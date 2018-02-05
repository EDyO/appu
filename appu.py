from pydub import AudioSegment
from pydub.silence import split_on_silence
import ConfigParser
import logging
import sys

# Using logger instead of print
l = logging.getLogger("pydub.converter")
l.addHandler(logging.StreamHandler())

# Debug mode with param -debug
if len(sys.argv) > 1 and str(sys.argv[1]) == "-debug" :
    l.setLevel(logging.DEBUG)

# read config file
configParser = ConfigParser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)
# Declares config parameters as variables
for section in configParser.sections():
    for name, value in configParser.items(section):
        globals()[name] = value

# Read mp3 tags from config file
mp3_tags={
    'title': title,
    'artist': artist,
    'album': album,
    'track': track,
    'comment': comment,
}

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

l.info("Importing podcast")
podcast = load_mp3(podcast_file)

l.info("Importing music")
song =  load_mp3(song_file)

l.info("Generating opening music")
opening = song[:20000]

l.info("Generating final music")
ending = song[-40000:]

#podcast = split_on_silence(podcast) <-- TODO

l.info("Normalizing podcast audio")

podcast = podcast.normalize()

l.info("Generating final podcast file: opening + podcast + ending")

final = opening.append(podcast, crossfade=1000)
final = final.append(ending,  crossfade=4000)

l.info("Exporting final file")

final.export(final_file, format="mp3", tags=mp3_tags, bitrate='48000', parameters=["-ac", "1"], id3v2_version='3', cover=cover_file)

l.info("Done! File {} generated correctly".format(final_file))
