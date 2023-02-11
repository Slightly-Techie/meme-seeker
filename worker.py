"""
worker that listens for mentions goes here
"""
import json

from tweepy import Stream

from util.utils import load_config
from util.logger_tool import Logger


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

    def on_request_error(self, status_code):
        print(status_code)
        Logger.debug(status_code)


if __name__ == "__main__":
    username = [load_config("twitter", "username")]
    stream = StreamWorker(
        load_config("twitter", "consumer_key"),
        load_config("twitter", "consumer_secret"),
        load_config("twitter", "access_token_default"),
        load_config("twitter", "access_secret_default")
        )
    stream.filter(track=username, threaded=True)
