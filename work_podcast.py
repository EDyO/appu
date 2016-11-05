from pydub import AudioSegment
from pydub.silence import split_on_silence

podcast = AudioSegment.from_mp3("/home/mitch/audio_tmp/podcast.mp3")
song =  AudioSegment.from_mp3("/home/mitch/audio_tmp/intro.mp3")

podcast = podcast.normalize()
#podcast = split_on_silence(podcast) <-- TODO


opening = song[:20000]

ending = song[-40000:]

final = opening.append(podcast, crossfade=1000)
final = final.append(ending,  crossfade=4000)
final.export("EDyO-19.mp3", format="mp3", parameters=["-ac", "1", "-ab", "48k", "-i", "logo.jpg"])
