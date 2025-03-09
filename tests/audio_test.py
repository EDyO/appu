from unittest import mock

import pytest
from pydub import AudioSegment

from appu2.audio import concat, normalize, split


MockAudioSegments = {}


class MockAudioSegment(object):
    def __init__(self, range_limit):
        self._segment = list(range(range_limit))

    @classmethod
    def from_mp3(cls, filename: str) -> None:
        this = cls(50000)
        MockAudioSegments[filename] = this
        return this

    def __len__(self) -> int:
        return len(self._segment)

    def __getitem__(self, slice_limit):
        return self._segment[slice_limit.start:slice_limit.stop:slice_limit.step]

    def append(self, another_segment, crossfade=0):
        new_segment = MockAudioSegment(len(self) + len(another_segment) - 2)
        new_segment._segment.append(self._segment)
        new_segment._segment.append(another_segment[crossfade:])
        return new_segment


def test_normalize(monkeypatch: pytest.MonkeyPatch) -> None:
    filename = "normalize.mp3"
    monkeypatch.setattr(AudioSegment, "from_mp3", MockAudioSegment.from_mp3)

    with mock.patch("pydub.effects.normalize") as pydub_normalize_method:
        normalize(filename)

    pydub_normalize_method.assert_called_once_with(MockAudioSegments[filename], headroom=-1.5)


def test_split(monkeypatch: pytest.MonkeyPatch) -> None:
    filename = "splitting.mp3"
    monkeypatch.setattr(AudioSegment, "from_mp3", MockAudioSegment.from_mp3)

    segment1, segment2 = split(filename, slice(0, 20000, None), slice(-30000, None, None))
    assert len(segment1) == 20000
    assert len(segment2) == 30000


def test_concat() -> None:
    intro_audio = MockAudioSegment.from_mp3("intro.mp3")
    master_audio = MockAudioSegment.from_mp3("master.mp3")

    resulting_audio = concat([(intro_audio, 0), (master_audio, 1000)])

    assert len(resulting_audio) == len(intro_audio) + len(master_audio)
