from pydub import AudioSegment
from pydub.silence import split_on_silence
import ConfigParser
import logging

l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())

configParser = ConfigParser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

#Read mp3 from mp3 file
mp3_tags={
    'title': configParser.get('tag-config','title'),
    'artist': configParser.get('tag-config','artist'),
    'album': configParser.get('tag-config','album'),
    'track': configParser.get('tag-config','track'),
    'comment': configParser.get('tag-config','comment'),
}

print "Importing podcast"
podcast = AudioSegment.from_mp3(configParser.get('files-config','podcast_file'))

print "Importing music"
song =  AudioSegment.from_mp3(configParser.get('files-config','song_file'))

print "Generating opening music"
opening = song[:20000]


print "Generating final music"
ending = song[-40000:]

print "Normalizing podcast audio"
podcast = podcast.normalize()
#podcast = split_on_silence(podcast) <-- TODO

print "Generating final podcast file: opening + podcast + ending"

final = opening.append(podcast, crossfade=1000)
final = final.append(ending,  crossfade=4000)

final.export(configParser.get('files-config','final_file'), format="mp3", tags=mp3_tags, bitrate='48000', parameters=["-ac", "1"], cover="files/homer.png")

print  configParser.get('tag-config','comment')

#final.export(configParser.get('files-config','final_file'), format="mp3", parameters=["-ac", "1", "-ab", "48k"])

print "Done"
