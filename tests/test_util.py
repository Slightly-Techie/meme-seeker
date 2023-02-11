"""
Test Cases for the functinos in utils
"""
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

from util.utils import load_config


class UtilTestCases(unittest.TestCase):
    """Test cases for functions"""

    def test_load_config_success(self):
        """Test config and return item"""
        config_result = load_config(
            "twitter",
            "username"
        )
        self.assertIsNotNone(config_result)

    def test_load_config_no_section(self):
        """Test section does not exist"""

        config_result = load_config(
            "instagram", "secret_key"
        )
        self.assertIsNone(config_result)

    def test_config_name_no_exist(self):
        """Test section exists but object name no exist"""

        config_result = load_config(
            "twitter", "somethingelse"
        )
        self.assertIsNone(config_result)
