"""
worker that listens for mentions goes here
"""
import json
from tweepy import (
    Stream,
    API, OAuthHandler
)
# import pika
from util.utils import load_config
from util.logger_tool import Logger

from functions import download_image


consumer_key = load_config("twitter", "consumer_key")
consumer_secret = load_config("twitter", "consumer_secret")
access_token = load_config("twitter", "access_token_default")
access_token_secret = load_config("twitter", "access_secret_default")

v1_auth = OAuthHandler(consumer_key, consumer_secret)
v1_auth.set_access_token(access_token, access_token_secret)
v1_api = API(v1_auth)


class StreamWorker(Stream):
    """Main worker that streams and listens for mentions"""

    def on_connect(self):
        Logger.info("Connection established for Streaming")

    def on_status(self, status):
        Logger.info(status)

    def on_data(self, raw_data):
        json_data = json.loads(raw_data)
        print(json_data)
        Logger.info(raw_data)
        if "in_reply_to_status_id_str" in json_data:
            tweet_data = self.get_orginal_tweet(
                json_data["in_reply_to_status_id_str"]
            )
        else:
            tweet_data = json_data
        response = download_image(tweet_data)
        if response is not None:
            send_sample_tweet(response)

    def on_request_error(self, status_code):
        print(status_code)
        Logger.debug(status_code)

    def get_orginal_tweet(self, tweet_id):
        Logger.info(tweet_id)
        original_tweet = v1_api.get_status(tweet_id)
        Logger.info(json.dumps(original_tweet._json))
        Logger.info(original_tweet.text)

        return original_tweet._json

    def on_disconnect(self):
        ''' Restart stream'''
        username = [load_config("twitter", "username")]
        stream = StreamWorker(
            load_config("twitter", "consumer_key"),
            load_config("twitter", "consumer_secret"),
            load_config("twitter", "access_token_default"),
            load_config("twitter", "access_secret_default")
            )
        stream.filter(track=username, threaded=True)



def send_sample_tweet(tweet_data):
    """Respond to tweet"""
    try:
        v1_api.update_status(
            "Done. Have a wonderful day.",
            in_reply_to_status_id=tweet_data[0]
        )
        Logger.info("Tweet Response sent sucessfully")
    except Exception as tweeting_error:
        Logger.fatal(tweeting_error)


if __name__ == "__main__":
    username = load_config("twitter", "username")
    stream = StreamWorker(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        )
    stream.filter(
        track=[username],
        threaded=True
    )
