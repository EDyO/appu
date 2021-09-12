import pytest
from botocore.exceptions import ClientError

from publish import upload_file


class MockS3Client(object):
    def upload_file(self, file_name, bucket, object_name):
        if bucket == "private-bucket":
            raise ClientError(
                {'Error':
                 {'Code': 'AccessDenied',
                  'Message': 'Access Denied'}},
                'PutObject',
            )


upload_file_cases = [
    ("podcast/episode.mp3", "existing-bucket", "podcast/episode.mp3", True),
    ("podcast/episode.mp3", "private-bucket", "podcast/episode.mp3", False),
]


@pytest.mark.parametrize(
    "file_name, bucket, object_name, expected_result",
    upload_file_cases,
)
def test_upload_file(
        file_name,
        bucket,
        object_name,
        expected_result,
        caplog,
):
    result = upload_file(file_name, bucket, object_name, MockS3Client())
    if not expected_result:
        assert "rror" in caplog.text
    assert result == expected_result
