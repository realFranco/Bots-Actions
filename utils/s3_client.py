"""
Dev: franco@systemagency.com
Date: Feb 28th, 2020

Module that serve files into S3 buckets.

Partial Documentation:

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
"""

import logging
import boto3
from botocore.exceptions import ClientError


class S3Client(object):

    def __init__(self):
        self.bucket_name = ''


    def upload_file(self, file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            # response = s3_client.upload_file(file_name, bucket, object_name)
            try:
                with open(file_name, 'rb') as f:
                    response = s3_client.upload_fileobj(
                        f, bucket, object_name,
                        ExtraArgs={
                            'ACL': 'public-read',
                            'ContentType': 'text/html'
                        }
                    )
                print(response) 
            except FileNotFoundError as err:
                print(err)
        except ClientError as e:
            logging.error(e)
            return False
        return True
        