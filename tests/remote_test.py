import os
from unittest import mock

import boto3

from appu2.remote import download_http, download_s3, upload


def mock_get(url: str, timeout: int, headers:dict=None):
    class MockResponse:
        def __init__(self):
            self.data = "SOME CONTENT"
            self.headers = headers

        @property
        def content(self):
            return self.data.encode()

    return MockResponse()


@mock.patch("boto3.session.Session.client")
def test_upload(client_mock: boto3.session.Session.client) -> None:
    filename = "episode.mp3"
    address = "s3://mypodcast-episodes/podcast/episode.mp3"

    upload(filename, address, s3_client=client_mock)

    client_mock.upload_file.assert_called_once_with(
        filename,
        "mypodcast-episodes",
        "podcast/episode.mp3",
    )


@mock.patch("boto3.session.Session.client")
def test_download_s3(client_mock: boto3.session.Session.client) -> None:
    address = "s3://mypodcast-masters/episode.master.mp3"

    with mock.patch("builtins.open") as m:
        downloaded_filename = download_s3(address, s3_client=client_mock)

    client_mock.download_fileobj.assert_called_once_with(
        "mypodcast-masters",
        "episode.master.mp3",
        mock.ANY,
    )
    m.assert_has_calls(
        [
            mock.call("episode.master.mp3", "wb"),
            mock.call().__enter__(),
            mock.call().__exit__(None, None, None),
        ],
    )
    assert downloaded_filename == "episode.master.mp3"


def test_download_http(monkeypatch) -> None:
    address = "https://some-site.com/some-file.mp3"
    monkeypatch.setattr("requests.get", mock_get)

    downloaded_filename = download_http(address)

    assert downloaded_filename == "some-file.mp3"
    downloaded_content = open(downloaded_filename)
    assert downloaded_content.read() == "SOME CONTENT"
    os.unlink(downloaded_filename)
