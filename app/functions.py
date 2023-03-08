"""
Functions for various actions to perform on the image/gif/video
"""
from threading import Thread
import mimetypes
import shutil
import uuid
import boto3
import requests
from db.operations import DbOperations
# from util.logger_tool import Logger
from util.utils import load_config


def download_image(data):
    """get the image file from the url"""
    if data["entities"]["media"][0]["media_url"]:
        media_url = data["entities"]["media"][0]["media_url"]
        response = requests.get(media_url)
        video_filename = None
        if data["extended_entities"]["media"][0]["video_info"]:
            video_url = data["extended_entities"]["media"][0][
                        "video_info"
                        ]["variants"][0]["url"]
            video_filename = save_video(
                video_url
            )
            video_thread = Thread(
                target=push_to_s3, args=(video_filename,))
            video_thread.start()
            video_thread.join()

        image_file = response.content
        img_format = mimetypes.guess_extension(
            response.headers.get('content-type').split(";")[0]
        )
        db_data = {
            "image_blob": image_file,
            "video_filename": video_filename,
            "image_url": media_url,
            "video_url": video_url,
            "tweet_id": data["id_str"]
        }

        DbOperations().save_image(
            db_data, img_format
            )
        return [data["id_str"], video_filename]
    else:
        pass


def save_video(video_url):
    """Save video to AWS S3 bucket"""
    video_info_url = video_url
    filename = uuid.uuid4().hex
    video_res = requests.get(video_info_url, stream=True)
    video_format = mimetypes.guess_extension(
        video_res.headers.get('content-type').split(";")[0]
    )

    with open(filename+video_format, "wb") as f:
        shutil.copyfileobj(video_res.raw, f)
    video_res.close()

    return filename+video_format


def push_to_s3(filename):
    """Push video/gif to S3"""
    bucket_name = load_config(
        "aws_credentials", "aws_storage_bucket"
    )
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=load_config(
            "aws_credentials", "aws_access_key"),
        aws_secret_access_key=load_config(
            "aws_credentials", "aws_secret_access_key"
        )
    )
    s3_client.upload_file(
        filename,
        bucket_name,
        filename
    )
    return


def send_tweet():
    """Tweet an image or gif"""
