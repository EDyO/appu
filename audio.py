import re
import requests
import os.path
from pydub import AudioSegment


def download_file(mp3_file_name, file_type):
    """
    This check if is a url and donwload the file
    in files directory with podcast.mp3 filename.
    """
    remotefile = requests.get(
        mp3_file_name,
        headers={"User-Agent": "Wget/1.19.4 (linux-gnu)"})
    # Set different file name if is jingle or podcast file.
    result_file = "files/{}.mp3".format(file_type)
    with open(result_file, 'wb') as output:
        output.write(remotefile.content)
    return result_file


def load_mp3(mp3_file_name, file_type='podcast'):
    """
    This tries to load the audio from a named mp3 file.
    It checks the filename has mp3 extension.
    """
    url_pattern = re.compile('^http[s]://')
    if url_pattern.match(mp3_file_name):
        mp3_file_name = download_file(mp3_file_name, file_type)
    if not mp3_file_name.lower().endswith('.mp3'):
        raise SystemExit(
            'Incorrect audio file format. The file must have .mp3 extension'
        )
    return AudioSegment.from_mp3(mp3_file_name)

def check_cover(cover_file):
    """
    Check if local cover file exist to avoid errors in transformation.
    """
    if not os.path.exists(cover_file):
        raise SystemExit(
            'Cover file not found.'
        )
    return cover_file


def get_jingles(song_file_name):
    """
    This function returns both starting and ending
    jingles.
    """
    song = load_mp3(song_file_name, "jingle")
    return song[:20000], song[-40000:]


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
