"""
The tiny stuff
"""
import json
import sys
import configparser
from .logger_tool import Logger


def load_config(section: str, name: str):
    """Change config from json to ini for configparser"""
    file = "config.ini"
    config = configparser.ConfigParser()
    config.read(file)

    return config[section][name]


def save_config(data: dict, file: str):
    with open(file, "w") as f:
        json.dump(data, f)


def print_err(err):
    output = str(err) + " on line " + str(sys.exc_info()[2].tb_lineno)
    Logger.fatal(output)
