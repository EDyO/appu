from pydub import AudioSegment
from pydub.silence import split_on_silence

print "Importing podcast"
podcast = AudioSegment.from_mp3("/home/mitch/AAE/podcast.mp3")

print "Importing music"
song =  AudioSegment.from_mp3("/home/mitch/AAE/intro.mp3")

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
final.export("EDyO-19.mp3", format="mp3", parameters=["-ac", "1", "-ab", "48k"])

print "Done"
