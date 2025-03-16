import boto3
import botocore
import requests
from loguru import logger


def upload(filename, address: str, s3_client: boto3.session.Session.client = None) -> None:
    if s3_client is None:
        s3_client = boto3.client("s3")

    logger.info(f"Uploading {filename} to {address}")

    bucket, *object_name = address.replace("s3://", "").split("/")
    try:
        response = s3_client.upload_file(filename, bucket, "/".join(object_name))
    except botocore.exceptions.ClientError as e:
        logger.error(f"{e}: {response}")


def download(address: str) -> str:
    if address.startswith("s3://"):
        downloaded_filename = download_s3(address)
    else:
        downloaded_filename = download_http(address)
    return downloaded_filename


def download_s3(address: str, s3_client: boto3.session.Session.client = None) -> str:
    """Download a file from an S3 bucket

    Arguments:
    address (string): S3 URL
    s3_client (boto3.session.Session.client): S3 client to use. If not
      specified one is created. This is only useful for testing.

    Returns:
    Downloaded file (string)
    """
    if s3_client is None:
        s3_client = boto3.client("s3")

    logger.info(f"Downloading {address} (Direct S3)")

    url_parts = address.split("/")
    bucket, object_parts = url_parts[2], url_parts[3:]
    object_name = "/".join(object_parts)
    filename = object_parts[-1]

    try:
        with open(filename, "wb") as data:
            s3_client.download_fileobj(bucket, object_name, data)
    except botocore.exceptions.NoCredentialsError as error:
        logger.error(error)

    return filename


def download_http(address: str) -> str:
    """Download a file from a regular HTTP URL

    Arguments:
    address (string): HTTP URL

    Returns:
    Downloaded file (string)
    """
    logger.info(f"Downloading {address} (regular HTTP)")
    remotefile = requests.get(
        address,
        headers={"User-Agent": "Wget/1.19.4 (linux-gnu)"},
        timeout=10,
    )
    filename = address.split("/")[-1]
    if "?" in filename:
        filename = filename.split("?")[-2]
    with open(filename, "wb") as output:
        output.write(remotefile.content)

    return filename
