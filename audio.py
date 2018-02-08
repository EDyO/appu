from pydub import AudioSegment

def load_mp3(mp3_file_name):
    """
    This tries to load the audio from a named mp3 file.
    It checks the filename has mp3 extension.
    """
    if mp3_file_name.lower().endswith('.mp3'):
        audio = AudioSegment.from_mp3(mp3_file_name)
    else:
        raise SystemExit(
            'Incorrect audio file format. The file must have .mp3 extension'
        )
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
