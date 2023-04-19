"""
Test Cases for the functinos in utils
"""
import pytest
from util.utils import load_config


def test_load_config_success():
    """Test config and return item"""
    config_result = load_config(
        "twitter",
        "username",
        file="app/config.ini"
    )
    assert config_result is not None


def test_load_config_no_section():
    """Test section does not exist"""

    config_result = load_config(
        "instagram", "secret_key", file="app/config.ini"
    )
    assert config_result is None


def test_config_name_no_exist():
    """Test section exists but object name no exist"""

    config_result = load_config(
        "twitter", "somethingelse", file="app/config.ini"
    )
    assert config_result is None
