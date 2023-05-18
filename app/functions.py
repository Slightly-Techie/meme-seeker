"""
Functions for various actions to perform on the image/gif/video
"""
from threading import Thread
import mimetypes
import shutil
import uuid
import hashlib
import boto3
import requests
from db.operations import DbOperations
from util.logger_tool import Logger
from util.utils import load_config


def download_image(data, tweet_id, tweet_text):
    """get the image file from the url"""
    Logger.info("Media download in progress.....")
    if "media" in data["includes"]:
        Logger.info("Found Media. Proceeding to download...")
        media_url = data["includes"]["media"][0]["preview_image_url"]
        response = requests.get(media_url)
        video_filename = None
        video_url = None
        if "variants" in data["includes"]["media"][0]:
            video_url = data["includes"]["media"][0]["variants"][0]["url"]
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
        hash_digest = hash_file(image_file)
        db_data = {
            "image_blob": image_file,
            "image_hash_digest": hash_digest,
            "video_filename": video_filename,
            "image_url": media_url,
            "video_url": video_url,
            "tweet_id": tweet_id
        }

        save_image_res = DbOperations().save_image(
            db_data, img_format, keyword_tag="".join(tweet_text.split()[1:])
            )
        if save_image_res == "Image exists":
            return "Image exists"
        return [tweet_id, video_filename]
    else:
        Logger.info("No media data found")
        pass


def get_image_file(tweet_text):
    """get the image blob and construct the image"""
    print(tweet_text)
    tweet_tag = "".join(tweet_text.split()[2])
    image_blob, image_filenanme = DbOperations().get_image(tweet_tag)
    return image_blob, image_filenanme


def save_video(video_url):
    """Save video to AWS S3 bucket"""
    Logger.info("Saving video as a file on local system")
    video_info_url = video_url
    filename = uuid.uuid4().hex
    video_res = requests.get(video_info_url, stream=True)
    video_format = mimetypes.guess_extension(
        video_res.headers.get('content-type').split(";")[0]
    )
    Logger.info("Filename: {}".format(filename+video_format))

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
    response = s3_client.upload_file(
        filename,
        bucket_name,
        filename
    )
    Logger.info("AWS S3 response: {}".format(response))
    return True


def hash_file(image_blob):
    """Hash the image blob"""
    Logger.info("Hash the blob and return the hash digest")
    hasher = hashlib.sha256()
    hasher.update(image_blob)
    Logger.info("Hashing complete!!")
    return hasher.hexdigest()
