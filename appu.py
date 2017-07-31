from pydub import AudioSegment
from pydub.silence import split_on_silence
import ConfigParser
import logging
import sys

#Debug mode with param -debug

if len(sys.argv) > 1 and str(sys.argv[1]) == "-debug" :
    l = logging.getLogger("pydub.converter")
    l.setLevel(logging.DEBUG)
    l.addHandler(logging.StreamHandler())

 #read config file

configParser = ConfigParser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

#Read mp3 tags from config file
mp3_tags={
    'title': configParser.get('tag-config','title'),
    'artist': configParser.get('tag-config','artist'),
    'album': configParser.get('tag-config','album'),
    'track': configParser.get('tag-config','track'),
    'comment': configParser.get('tag-config','comment'),
}

cover_file=configParser.get('files-config','cover_file')


print "Importing podcast"

audio_file = configParser.get('files-config','podcast_file')

if audio_file.lower().endswith('.mp3'):
    podcast = AudioSegment.from_mp3(audio_file)
else:
    sys.exit('Incorrect audio file format. The file must have .mp3 extension')


print "Importing music"
song =  AudioSegment.from_mp3(configParser.get('files-config','song_file'))

print "Generating opening music"
opening = song[:20000]


print "Generating final music"
ending = song[-40000:]

#podcast = split_on_silence(podcast) <-- TODO

print "Normalizing podcast audio"

final = final.normalize()

print "Generating final podcast file: opening + podcast + ending"

final = opening.append(podcast, crossfade=1000)
final = final.append(ending,  crossfade=4000)

print "Exporting final file"

final.export(configParser.get('files-config','final_file'), format="mp3", tags=mp3_tags, bitrate='48000', parameters=["-ac", "1"], id3v2_version='3', cover=cover_file)

print "Done! File %s generated correctly" %configParser.get('files-config','final_file')
