import pydub


def normalize(filename: str) -> pydub.AudioSegment:
    """
    This function normalizes track.
    """
    audio = pydub.AudioSegment.from_mp3(filename)

    return pydub.effects.normalize(audio, headroom=-1.5)


def split(filename: str, *slices_limits: list[str]) -> list[pydub.AudioSegment]:
    """
    This function splits track into as many slices as defined.
    """
    audio = pydub.AudioSegment.from_mp3(filename)
    slices = []
    for slice_limit in slices_limits:
        slices.append(audio[slice_limit])

    return slices


def concat(audios):
    """
    This function concatenates all the audios.
    """
    final = audios[0][0]
    for audio, fade in audios[1:]:
        final = final.append(audio, crossfade=fade)

    return final
