import pytest
import loader module
import sys, os
import modules from src
import package/module from src

rpath = os.path.abspath('..')
if rpath not in sys.path:
    sys.path.insert(0, rpath)

from src.loader import SlackDataLoader
from src.draw import Visualize
import src.utils as utils

def test_parse_slack_reaction():
    path_channel = "/home/biniyam/tenx-tasks/tenxdata/"
    channel = "random"

    parsed_data = SlackDataLoader.parse_slack_reaction(path_channel, channel)

    assert parsed_data is not None
    assert isinstance(parsed_data, type)


