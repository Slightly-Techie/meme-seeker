"""
worker that listens for mentions goes here
"""
import json
from tweepy import StreamingClient, Client, StreamRule
# import pika
import requests
from util.utils import load_config
from util.logger_tool import Logger

from functions import download_image

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
            tweet_data = self.get_orginal_tweet(
                json_data["data"]["referenced_tweets"][0]["id"]
            )
        else:
            tweet_data = json_data

        response = download_image(tweet_data, json_data["data"]["id"], username=tweet_username)

        if response is not None:
            send_sample_tweet(json_data)

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
