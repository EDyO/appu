from pydub import AudioSegment

import pytest

from audio import load_mp3, get_jingles, glue_tracks

class MockAudioSegment(object):
    @classmethod
    def from_mp3(self, file_name):
        self._segment = range(50000)
        return self()

    def __len__(self):
        return len(self._segment)

def test_load_mp3(monkeypatch):
    original_name = 'original.mp3'
    monkeypatch.setattr(AudioSegment, 'from_mp3', MockAudioSegment.from_mp3)
    audio_segment = load_mp3(original_name)
    assert len(audio_segment) == 50000

def test_load_mp4_fails(monkeypatch):
    original_name = 'original.mp4'
    monkeypatch.setattr(AudioSegment, 'from_mp3', MockAudioSegment.from_mp3)
    with pytest.raises(SystemExit) as sys_exit:
        audio_segment = load_mp3(original_name)
    assert 'The file must have .mp3 extension' in str(sys_exit)
