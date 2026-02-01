import re
import logging
import os
import requests
import boto3
from botocore.exceptions import ClientError
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import detect_silence

def download_file(mp3_file_name, file_type):
    """
    This check if is a url and download the file
    in files directory with podcast.mp3 filename.
    """
    remotefile = requests.get(
        mp3_file_name,
        headers={"User-Agent": "Wget/1.19.4 (linux-gnu)"})
    # Set different file name if is jingle or podcast file.
    result_file = "files/{}.mp3".format(file_type)
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, 'wb') as output:
        output.write(remotefile.content)
    return result_file


def download_file_from_s3(s3_url, s3_client=None):
    """Download a file from an S3 bucket

    Arguments:
    s3_url (string): URL
    s3_client (boto3.session.Session.client): S3 client to use. If not
      specified one is created. This is only useful for testing.

    Returns:
    string: File downloaded
    """

    # If no S3 client was specified, create a new one.
    if s3_client is None:
        s3_client = boto3.client('s3')

    url_parts = s3_url.split("/")
    bucket, object_parts = url_parts[2], url_parts[3:]
    object_name = "/".join(object_parts)
    file_name = "files/{}".format(object_parts[-1])

    # Download the file, catching possible errors.
    with open(file_name, 'wb') as data:
        s3_client.download_fileobj(bucket, object_name, data)

    return file_name


def load_mp3(mp3_file_name, file_type='podcast'):
    """
    This tries to load the audio from a named mp3 file.
    It checks the filename has mp3 extension.
    """
    url_pattern = re.compile('^http[s]://')
    s3_pattern = re.compile('^s3://')
    if url_pattern.match(mp3_file_name):
        mp3_file_name = download_file(mp3_file_name, file_type)
    elif s3_pattern.match(mp3_file_name):
        mp3_file_name = download_file_from_s3(mp3_file_name)
    if not mp3_file_name.lower().endswith('.mp3'):
        raise SystemExit(
            'Incorrect audio file format. The file must have .mp3 extension'
        )
    return AudioSegment.from_mp3(mp3_file_name)


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

def normalize_audio(podcast_file):
    """
    This function normalize track
    """
    return normalize(podcast_file, headroom=-1.5)


def clamp_silence(audio, max_silence_ms=500, silence_thresh=None):
    """
    Limit stretches of silence to a maximum duration.
    Any silent region longer than max_silence_ms is replaced
    with exactly max_silence_ms of silence.
    """
    if max_silence_ms <= 0:
        return audio

    if silence_thresh is None:
        silence_thresh = audio.dBFS - 16

    silent_ranges = detect_silence(
        audio,
        min_silence_len=max_silence_ms + 1,
        silence_thresh=silence_thresh,
    )

    if not silent_ranges:
        return audio

    output = AudioSegment.empty()
    cursor = 0
    for start, end in silent_ranges:
        output += audio[cursor:start]
        output += AudioSegment.silent(duration=max_silence_ms)
        cursor = end

    output += audio[cursor:]
    return output


def add_tail_silence(audio, duration_ms=2000):
    """Append silence at the end of the track."""
    if duration_ms <= 0:
        return audio
    return audio + AudioSegment.silent(duration=duration_ms)
