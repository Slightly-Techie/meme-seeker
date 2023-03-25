"""
The tiny stuff
"""
import json
import sys
import configparser
from .logger_tool import Logger


def load_config(section: str, name: str, file="config.ini"):
    """Change config from json to ini for configparser"""
    try:
        file = "config.ini"
        config = configparser.RawConfigParser()
        config.read(file)

        return config[section][name]
    except FileNotFoundError as file_err:
        Logger.debug(file_err)
        return None
    except KeyError as key_err:
        Logger.debug(key_err)
        return None


def save_config(data: dict, file: str):
    with open(file, "w") as f:
        json.dump(data, f)


def print_err(err):
    output = str(err) + " on line " + str(sys.exc_info()[2].tb_lineno)
    Logger.fatal(output)
