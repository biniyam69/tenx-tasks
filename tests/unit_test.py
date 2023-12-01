import os
import sys

import pytest

rpath = os.path.abspath('..')
if rpath not in sys.path:
    sys.path.insert(0, rpath)

import src.utils as utils
from src.draw import Visualize
from src.loader import SlackDataLoader


def test_parse_slack_reaction():
    path_channel = "/home/biniyam/tenx-tasks/tenxdata/"
    channel = "random"

    parsed_data = SlackDataLoader.parse_slack_reaction(path_channel, channel)

    assert parsed_data is not None
    assert isinstance(parsed_data, type)


