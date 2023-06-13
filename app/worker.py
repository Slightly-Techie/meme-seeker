"""
worker that listens for mentions goes here
"""
import json
# import io
import os
# from PIL import Image
from tweepy import (
    StreamingClient, Client, StreamRule, API,
    OAuthHandler,
    # parsers
)
# import pika
import requests
from util.utils import load_config
from util.logger_tool import Logger

from functions import (
    download_image,
    # get_image_file,
    get_s3_video_file
)

bearer_token = load_config("twitter", "bearer_token")
consumer_key = load_config("twitter", "consumer_key")
consumer_secret = load_config("twitter", "consumer_secret")
access_token = load_config("twitter", "access_token_default")
access_token_secret = load_config("twitter", "access_secret_default")
base_url = load_config("twitter", "base_url")

tweet_client = Client(
    bearer_token=bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    wait_on_rate_limit=True
    )


class StreamWorker(StreamingClient):
    """Main worker that streams and listens for mentions"""

    def on_connect(self):
        Logger.info("Connection established for Streaming")

    def on_status(self, status):
        Logger.info(status)

    def on_data(self, raw_data):
        json_data = json.loads(raw_data)
        print(json_data)
        Logger.info(raw_data)

        # Get username of the tweet mention
        tweet_username = (
            json_data["includes"]["users"][0]["username"] if json_data["includes"]["users"][0] else "Test User"
        )

        # self.publish_to_queue(raw_data)
        if "referenced_tweets" in json_data["data"]:
            tweet_text = json_data["data"]["text"]
            text_list = [
                t for t in tweet_text.split() if not t.startswith(("@", "http"))
                ]
            extract_text = " ".join(text_list)
            print(text_list)
            if text_list[0] == "get":
                extract_text = " ".join(text_list[1:])
                print(extract_text)
                filename = get_s3_video_file(
                    extract_text
                )
                media_id = upload_media_v1(filename, filename)
                if media_id:
                    tweet_with_image(
                        media_id, json_data["data"]["id"], filename
                        )
                else:
                    Logger.debug("No media id found")
            else:
                tweet_data = self.get_orginal_tweet(
                    json_data["data"]["referenced_tweets"][0]["id"]
                )
                response = download_image(
                    tweet_data, json_data["data"]["id"],
                    tweet_text=extract_text
                    )

                if response is not None:
                    send_sample_tweet(json_data)
        else:
            pass

    def on_request_error(self, status_code):
        print(status_code)
        Logger.debug(status_code)

    def get_orginal_tweet(self, tweet_id):
        Logger.info(tweet_id)
        original_tweet_res = requests.get(
            base_url + "/tweets/{}".format(tweet_id),
            params={
                "expansions": "attachments.media_keys,entities.mentions.username",
                "tweet.fields": "entities",
                "media.fields": "variants,preview_image_url"
            },
            headers={"Authorization": "Bearer {}".format(bearer_token)}
        )
        original_tweet = original_tweet_res.json()
        # Logger.info(original_tweet["data"])
        Logger.info(json.dumps(original_tweet))
        return original_tweet

    def on_disconnect(self):
        ''' Restart stream'''
        start_tweet_stream()

    # def on_connection_error(self, err):
    #     # Handle when connection times ouut
    #     print(err)
    #     super().on_connection_error()
    #     start_tweet_stream()

    # def on_exception(self, exception):
    #     super().on_exception(exception)
    #     start_tweet_stream()


def upload_media_v1(image_data, filename):
    """Using v1 endpoint to upload media
      use the ID from response in tweet"""
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    Logger.info("Uploading the media named {} on v1 API".format(filename))
    # image = Image.open(io.BytesIO(image_data))
    # image.save(filename)
    if os.path.exists(filename):
        res = api.media_upload(
            filename
        )
        Logger.info(res)
        return res.media_id_string
    else:
        return None


def tweet_with_image(media_id, tweet_id, filename):
    """Tweet with image ID"""
    try:
        Logger.info("Sending the tweet with image")
        tweet_client.create_tweet(
            text=".",
            in_reply_to_tweet_id=tweet_id,
            media_ids=[media_id]
        )
    except Exception as tweet_excpetion:
        Logger.debug(tweet_excpetion)
    finally:
        os.remove(filename)


def send_sample_tweet(tweet_data):
    """Respond to tweet"""
    try:
        tweet_client.create_tweet(
            text="Done. Have a wonderful day.",
            in_reply_to_tweet_id=tweet_data["data"]["id"],
            )
        Logger.info("Tweet Response sent sucessfully")
    except Exception as tweeting_error:
        Logger.fatal(tweeting_error)


def start_tweet_stream():
    username = load_config("twitter", "username")
    stream = StreamWorker(
        bearer_token=bearer_token
        )
    stream.add_rules(StreamRule(username))
    stream.filter(
        expansions=[
            "referenced_tweets.id",
            "referenced_tweets.id.author_id",
            "attachments.media_keys"
        ],
        user_fields=[
            "entities",
        ],
        media_fields=[
            "preview_image_url",
            "variants"
        ],
        tweet_fields=[
            "entities"
        ],
        threaded=True
    )


if __name__ == "__main__":
    start_tweet_stream()
