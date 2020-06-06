import logging
import boto3
from botocore.exceptions import ClientError


def upload_file(file_name, bucket, object_name=None, s3_client=None):
    """Upload a file to an S3 bucket

    Arguments:
    file_name (string): File to upload
    bucket (string): Bucket to upload to
    object_name (string): S3 object name. If not specified then file_name
      is used
    s3_client (boto3.session.Session.client): S3 client to use. If not
      specified one is created. This is only useful for testing.

    Returns:
    boolean: True if file was uploaded, else False
    """

    # If no S3 client was specified, create a new one.
    if s3_client is None:
        s3_client = boto3.client('s3')

    # If S3 object_name was not specified, use file_name.
    if object_name is None:
        object_name = file_name

    # Upload the file, catching possible errors.
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
