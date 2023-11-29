import os
import sys

import pytest

rpath = os.path.abspath('..')
if rpath not in sys.path:
    sys.path.insert(0, rpath)
from src.loader import SlackDataLoader

paths = [
    '/home/biniyam/tenx-tasks/tenxdata/all-week8',
    '/home/biniyam/tenx-tasks/tenxdata/all-week9'
]



def test_slack_parser():
    df_slack = SlackDataLoader.slack_parser(paths)

    #expected columns
    expected_columns = [
        'msg_type', 'msg_content', 'sender_name', 'msg_sent_time', 'msg_dist_type',
        'time_thread_start', 'reply_count', 'reply_users_count', 'reply_users', 
        'tm_thread_end', 'channel'
    ]

    actual_cols = df_slack.columns.tolist()

    for column in expected_columns:
        assert column in actual_cols, f"Column {column} not found in df_slack"

    # #expected data types

    # expected_dtypes = {
    #     'msg_type': str, 'msg_content': str, 'sender_name': str, 'msg_sent_time': str,
    #     'msg_dist_type': str, 'time_thread_start': str, 'reply_count': int, 
    #     'reply_users_count': int, 'reply_users': str, 'tm_thread_end': str, 'channel': str
    # } 

    # for dtype in expected_dtypes:
    #     assert df_slack[dtype].dtype == expected_dtypes[dtype], f"Column {dtype} has wrong dtype"

    