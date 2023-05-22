"""
Testing the helper functions
"""
import pytest
import boto3
from util.utils import load_config
from unittest.mock import patch, MagicMock
from functions import (
    download_image, save_video, push_to_s3
)
from moto import mock_s3

request_result = MagicMock()
request_result.status_code = 200
request_result.content = b'test image'


initial_tweet_data = open("test_data/initial_tweet_data.json").read()
tweet_data = open("test_data/tweet_data.json").read()


@patch('app.functions.mimetypes.guess_extension', return_value=".png")
@patch('app.functions.push_to_s3')
@patch('app.functions.save_video', return_value="test_filename.png")
@patch('app.functions.requests')
def test_download_image(request_mock, save_video_mock, push_to_s3_mock, mime_mock):
    request_mock.get.return_value = request_result

    tweet_username = (
            initial_tweet_data["includes"]["users"][0]["username"] if initial_tweet_data["includes"]["users"][0] else "Test User"
        )

    download_image(tweet_data, initial_tweet_data["data"]["id"], tweet_username)


# Test save video function
@patch('app.functions.shutil')
@patch('app.functions.requests')
def test_save_video(request_mock, shutil_mock):
    request_result = MagicMock()
    request_result.status_code = 200
    request_result.headers = {'content-type': 'video/mp4'}

    request_mock.get.return_value = request_result

    video_url = "https://www.youtube.com/watch?v=xT4SV7AH3G8"

    filename = save_video(video_url)

    print(filename)


@mock_s3
def test_push_to_s3():
	filename = 'e892ede7dcfb4a599a053e4e17098788.mp4'
	conn = boto3.resource("s3", region_name="us-east-1")

	bucket_name = load_config(
		"aws_credentials", "aws_storage_bucket"
	)

	conn.create_bucket(Bucket=bucket_name)
	push_to_s3(filename)
