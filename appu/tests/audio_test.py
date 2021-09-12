import os
import pytest
from pydub import AudioSegment
from audio import download_file, load_mp3, get_jingles, glue_tracks


class MockAudioSegment(object):
    @classmethod
    def from_mp3(self, file_name):
        self._segment = list(range(50000))
        return self()

    def __len__(self):
        return len(self._segment)

    def __getitem__(self, val):
        return self._segment[val]

    def append(self, segment, crossfade=None):
        total = MockAudioSegment()
        total._segment.extend(segment._segment)
        return total


def mock_download_file(file_name, file_type='podcast'):
    return "files/{}.mp3".format(file_type)


def mock_get(url, headers={}):
    class MockResponse:
        def __init__(self):
            self.data = 'SOME CONTENT'
            self.headers = headers

        @property
        def content(self):
            return self.data.encode()

    return MockResponse()


def test_load_mp3(monkeypatch):
    original_name = 'original.mp3'
    monkeypatch.setattr(AudioSegment, 'from_mp3', MockAudioSegment.from_mp3)
    audio_segment = load_mp3(original_name)
    assert len(audio_segment) == 50000


def test_load_mp3_url(monkeypatch):
    original_name = 'https://service.com/original.mp3'
    monkeypatch.setattr(AudioSegment, 'from_mp3', MockAudioSegment.from_mp3)
    monkeypatch.setattr('audio.download_file', mock_download_file)
    audio_segment = load_mp3(original_name)
    assert len(audio_segment) == 50000


def test_load_mp4_fails(monkeypatch):
    original_name = 'original.mp4'
    monkeypatch.setattr(AudioSegment, 'from_mp3', MockAudioSegment.from_mp3)
    with pytest.raises(SystemExit) as sys_exit:
        load_mp3(original_name)
    assert 'The file must have .mp3 extension' in str(sys_exit)


def test_download_file(monkeypatch, tmpdir):
    original_name = 'http://service.com/original.mp3'
    monkeypatch.setattr('requests.get', mock_get)
    downloaded_file = download_file(original_name, 'podcast')
    assert downloaded_file == 'files/podcast.mp3'
    downloaded_content = open(downloaded_file)
    assert downloaded_content.read() == 'SOME CONTENT'
    os.unlink('files/podcast.mp3')


def test_get_jingles(monkeypatch):
    song_name = 'song.mp3'
    monkeypatch.setattr(AudioSegment, 'from_mp3', MockAudioSegment.from_mp3)
    begin, end = get_jingles(song_name)
    assert len(begin) == 20000
    assert len(end) == 40000
    assert begin == list(range(20000))
    assert end == list(range(10000, 50000))


def test_glue_tracks(monkeypatch):
    first = MockAudioSegment.from_mp3("whatever")
    second = MockAudioSegment.from_mp3("Anything else")
    final = glue_tracks([(first, 0), (second, 1000)])
    assert len(final) == 100000
