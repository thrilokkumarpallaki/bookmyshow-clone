import os
import tempfile
from typing import Any
from datetime import datetime, timedelta

import boto3
from boto3.s3.transfer import TransferConfig
from botocore import client
from pydantic import validate_arguments

from flask import jsonify, make_response, Response
from werkzeug.datastructures import FileStorage, ImmutableMultiDict
from werkzeug.utils import secure_filename

from log_util import get_logger

logger = get_logger(__name__)

MOVIE_DATA_S3_BUCKET = os.environ['movie_data_s3_bucket']
AWS_REGION = os.environ['aws_region']
ALLOWED_FILE_EXTENSIONS = {'JPEG': 'image', 'JPG': 'image', 'PNG': 'image', 'MP4': 'video', 'MOV': 'video'}


def create_response(resp_json, status=200) -> Response:
    resp = jsonify(resp_json)
    return make_response(resp, status)


def allowed_file_formats(file_name: str) -> tuple[bool, Any | None, Any | None]:
    is_allowed, file_type, file_ext = False, None, None
    if file_name is not None:
        _, file_ext = file_name.rsplit('.')
        file_type = ALLOWED_FILE_EXTENSIONS.get(file_ext.upper())
        if file_type:
            is_allowed = True
    return is_allowed, file_type, file_ext


@validate_arguments
def parse_movie_file_data(files: ImmutableMultiDict, movie_name) :
    file_data_dict = {}
    movie_name = secure_filename(movie_name)
    for idx, file in enumerate(files, start=1):
        file_data = files[file]
        is_allowed, file_type, file_ext = allowed_file_formats(file_data.filename)
        if is_allowed:
            tmp_file_name = secure_filename(filename=file_data.filename)
            if tmp_file_name == '':
                tmp_file_name = f'{movie_name}_{file_type}_{idx}.{file_ext.lower()}'
            file_data_dict[tmp_file_name] = [file_data, file_type]
        else:
            pass

    # store movie files in s3
    return save_movie_data_in_s3(file_data_dict, movie_name)


def save_movie_data_in_s3(file_data_dict: dict, movie_name: str) -> dict[str, list]:
    s3_object_urls = {'video_urls': [], 'image_urls': []}
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION, verify=False)
        for key in file_data_dict:
            file_data, file_type = file_data_dict[key]

            # save file in tmp location and read the file path.
            tmp_file_path = save_file_temp_location(key, file_data)
            s3_file_path = f'{movie_name}/{key}'
            s3_client.upload_file(tmp_file_path, MOVIE_DATA_S3_BUCKET, s3_file_path,
                                  Config=TransferConfig())
            object_url = construct_s3_object_url(s3_key=s3_file_path)
            if file_type == 'video':
                s3_object_urls['video_urls'].append(object_url)
            else:
                s3_object_urls['image_urls'].append(object_url)
            logger.info(f'File data for file {key} uploaded to s3 location {s3_file_path} successfully!')
    except Exception as e:
        logger.exception(e, exc_info=True)
    return s3_object_urls


def save_file_temp_location(file_name: str, file_data: FileStorage) -> str:
    file_path = None
    try:
        # create a temp directory to store movie media files
        tmp_dir_path = tempfile.gettempdir()
        file_path = os.path.join(tmp_dir_path, file_name)

        # Write the file to location
        file_data.save(file_path)
    except Exception as e:
        logger.exception(e, exc_info=True)
    return file_path


def construct_s3_object_url(s3_key: str) -> str:
    """
    This method constructs s3 object url for the uploaded files.
    It takes s3_key as parameter.
    :param s3_key: Object location in s3.
    :return: s3 object url.
    """
    s3_object_url = f'https://{MOVIE_DATA_S3_BUCKET}.S3.{AWS_REGION}.amazonaws.com/{s3_key}'
    return s3_object_url


def generate_pre_signed_s3_url(s3_object_urls: str):
    pre_signed_urls = []

    for s3_object_url in s3_object_urls:
        url_split = s3_object_url.split('/')

        # s3 object path is between domain and file.
        object_key = '/'.join(url_split[3:])
        try:
            s3_client = boto3.client('s3', region_name=AWS_REGION, config=client.Config(signature_version='s3v4'))
            pre_signed_url = s3_client.generate_presigned_url(ClientMethod='get_object',
                                                              Params={
                                                                  'Bucket': MOVIE_DATA_S3_BUCKET,
                                                                  'Key': object_key
                                                              },
                                                              ExpiresIn=3600)
            pre_signed_urls.append(pre_signed_url)
        except Exception as e:
            logger.exception(e, exc_info=True)
    return pre_signed_urls
