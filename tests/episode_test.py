import datetime

from appu2.episode import Episode


def test_episode() -> None:
    data = {
        "album": "Album",
        "artist": "Artist",
        "bucket": "mypodcast-episodes",
        "cover": "https://mypodcast.com/cover.png",
        "distributionID": "XXXXXXXXX",
        "episodeURL": "https://mypodcast.com/episodes/episode.mp3",
        "image": "",
        "intro": "https://mypodcast.com/intro.mp3",
        "links": [""],
        "master": "s3://mypodcast-masters/master/epidode.master.mp3",
        "pubDate": datetime.datetime(2000, 10, 10),
        "summary": "",
        "title": "Title",
        "trackNo": 100,
    }

    episode = Episode(**data)

    assert episode.title == "Title"
    assert episode.tags["title"] == "Title"
    assert episode.tags["artist"] == "Artist"
    assert episode.tags["album"] == "Album"
    assert episode.tags["track"] == 100
    assert episode.tags["comment"] == ""
    assert episode.filename == "episode.mp3"
    assert episode.destination == "s3://mypodcast-episodes/episodes/episode.mp3"
