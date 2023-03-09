"""
worker that listens for mentions goes here
"""
import json
from tweepy import Stream, Client
import pika
from util.utils import load_config
from util.logger_tool import Logger

from functions import download_image


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
        # self.publish_to_queue(raw_data)
        response = download_image(json_data)
        send_sample_tweet(response)

    def on_request_error(self, status_code):
        print(status_code)
        Logger.debug(status_code)

    def publish_to_queue(self, data):
        """On data, send to RabbitMQ queue"""
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                "rabbitmq"
            )
        )
        channel = conn.channel()
        channel.basic_publish(
            exchange="",
            routing_key="meme_queue",
            body=data
        )

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
    # Authenticate with Twitter's Client
    consumer_key = load_config("twitter", "consumer_key")
    consumer_secret = load_config("twitter", "consumer_secret")
    access_token = load_config("twitter", "access_token_default")
    access_token_secret = load_config("twitter", "access_secret_default")

    tweet_auth = Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True
        )
    # tweet_auth.set_access_token(access_token, access_token_secret)

    # api = API(tweet_auth)

    tweet_auth.create_tweet(
        text="Done. Have a wonderful day.",
        in_reply_to_tweet_id=tweet_data[0],
        )


if __name__ == "__main__":
    username = [load_config("twitter", "username")]
    stream = StreamWorker(
        load_config("twitter", "consumer_key"),
        load_config("twitter", "consumer_secret"),
        load_config("twitter", "access_token_default"),
        load_config("twitter", "access_secret_default")
        )
    stream.filter(track=username, threaded=True)
