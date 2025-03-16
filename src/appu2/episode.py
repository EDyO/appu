import datetime

import yaml
from pydantic import BaseModel, Field


class Episode(BaseModel):
    """Episode data."""
    album: str
    artist: str
    bucket: str
    cover: str
    distribution_id: str = Field(alias="distributionID")
    episode_url: str = Field(alias="episodeURL")
    image: str
    intro: str
    links: list[str]
    master: str
    pub_date: datetime.datetime = Field(alias="pubDate")
    summary: str
    title: str
    track_no: int = Field(alias="trackNo")

    @property
    def tags(self) -> dict:
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "track": self.track_no,
            "comment": self.summary,
        }

    @property
    def filename(self) -> str:
        return self.episode_url.split("/")[-1]

    @property
    def destination(self) -> str:
        return f"s3://{self.bucket}/{"/".join(self.episode_url.replace("https://", "").split("/")[1:])}"


def load_episode(episode_yaml: str) -> Episode:
        with open(episode_yaml, "r") as stream:
            data = yaml.safe_load(stream)

        return Episode(**data)
