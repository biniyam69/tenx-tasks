import argparse
import copy
import datetime
import glob
import io
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from time import sleep

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from nltk.corpus import stopwords
from pick import pick
from wordcloud import WordCloud


# Create wrapper classes for using slack_sdk in place of slacker
class SlackDataLoader:
    '''
    Slack exported data IO class.

    When you open slack exported ZIP file, each channel or direct message 
    will have its own folder. Each folder will contain messages from the 
    conversation, organised by date in separate JSON files.

    You'll see reference files for different kinds of conversations: 
    users.json files for all types of users that exist in the slack workspace
    channels.json files for public channels, 
    
    These files contain metadata about the conversations, including their names and IDs.

    For secruity reason, we have annonymized names - the names you will see are generated using faker library.
    
    '''
    def __init__(self, path):
        '''
        path: path to data
        '''
        self.path = "/home/biniyam/tenx-tasks/tenxdata"
        self.channels = self.get_channels()
        self.users = self.get_users()

    

    def get_users(self):
        '''
        write a function to get all the users from the json file
        '''

        with open(os.path.join(self.path, 'users.json'), 'r') as f:
            users = json.load(f)

        return users

    
    def get_channels(self):
        '''
        write a function to get all the channels from the json file
        '''
        with open(os.path.join(self.path, 'channels.json'), 'r') as f:
            channels = json.load(f)
        

        return channels

    def get_channel_messages(self, channel_name):
        '''
        write a function to get all the messages from a channel
        
        '''
        messages = []
        channel_id = None
        for channel in self.channels:
            if channel['name'] == channel_name:
                channel_id = channel['id']
                break
        if channel_id is None:
            raise Exception('Channel not found')
        for file in os.listdir(os.path.join(self.path, channel_id)):
            if file.endswith('.json'):
                with open(os.path.join(self.path, channel_id, file), 'r') as f:
                    messages.extend(json.load(f))
        return messages


    # 
    def get_user_map(self):
        '''
        write a function to get a map between user id and user name
        '''

        userNamesById = {}
        userIdsByName = {}
        for user in self.users:
            userNamesById[user['id']] = user['name']
            userIdsByName[user['name']] = user['id']
        return userNamesById, userIdsByName  



    '''

    Below are the functions used to parse data from the json files that were given

    Brought here from the original notebook parse_slack_data.ipynb, as an action of restructuring the codebase.

        From a single slack message, we can get

    1. The message 
    2. Type (message, file, link, etc) 
    3. The sender_id (assigned by slack) 
    4. The time the message was sent 
    5. The team (i don't know what that is now) 
    6. The type of the message (broadcast message, inhouse, just messgae) 
    7. The thread the message generated (from here we can go): 
        7.1 Text/content of the message 
        7.2 The thread time of the message 
        7.3 The thread count (reply count) 
        7.4 The number of user that reply the message (count of users that participated in the thread) 
        7.5 The time the last thread message was sent  
        7.6 The users that participated in the thread (their ids are stored as well) 
        s

    Columns we can get from a slack message:

    message_type, message_content, sender_id, time_sent, message_distribution,
    time_thread_start, reply_count, reply_user_count, time_thread_end, reply_users
    
    
    '''

    # combine all json file in all-weeks8-9
    @staticmethod
    def slack_parser(paths):
        """Parse Slack data to extract useful information from JSON files."""
        
        #initialize lists to store extracted data
        all_data = {
            'msg_type': [], 'msg_content': [], 'sender_name': [],
            'msg_sent_time': [], 'msg_dist_type': [], 'time_thread_start': [],
            'reply_count': [], 'reply_users_count': [], 'reply_users': [],
            'tm_thread_end': [], 'channel': []
        }
        
        for path_channel in paths:
            # Get all JSON file paths in the specified directory
            json_files = glob.glob(f"{path_channel}/*.json")
            
            # loop through each JSON file path
            for file_path in json_files:
                with open(file_path, 'r', encoding="utf8") as file:
                    json_data = json.load(file)

                    for row in json_data:
                        all_data['msg_type'].append(row.get('type', ''))
                        all_data['msg_content'].append(row.get('text', ''))
                        all_data['sender_name'].append(row.get('user_profile', {}).get('real_name', 'Not provided'))
                        all_data['msg_sent_time'].append(row.get('ts', ''))
                        if 'blocks' in row and row['blocks']:
                            block = row['blocks'][0]
                            if 'elements' in block and block['elements']:
                                element = block['elements'][0]
                                if 'elements' in element and element['elements']:
                                    all_data['msg_dist_type'].append(element['elements'][0].get('type', 'reshared'))
                                else:
                                    all_data['msg_dist_type'].append('reshared')
                            else:
                                all_data['msg_dist_type'].append('reshared')
                        else:
                            all_data['msg_dist_type'].append('reshared')
                        all_data['time_thread_start'].append(row.get('thread_ts', 0))
                        all_data['reply_users'].append(",".join(row.get('reply_users', [])))
                        all_data['reply_count'].append(row.get('reply_count', 0))
                        all_data['reply_users_count'].append(row.get('reply_users_count', 0))
                        all_data['tm_thread_end'].append(row.get('latest_reply', 0))
                        all_data['channel'].append(file_path.split('/')[-2])  # Extract channel from file path

        #create DataFrame from the extracted data
        df = pd.DataFrame(all_data)
        df = df[df['sender_name'] != 'Not provided'].reset_index(drop=True)
        columns = ['msg_type', 'msg_content', 'sender_name', 'msg_sent_time', 'msg_dist_type', 'time_thread_start', 'reply_count', 'reply_users_count', 'reply_users', 'tm_thread_end', 'channel']
        df = df[columns]
        df['msg_sent_time'] = pd.to_datetime(df['msg_sent_time'], unit='s')
        df['time_thread_start'] = pd.to_datetime(df['time_thread_start'], unit='s')
        df['tm_thread_end'] = pd.to_datetime(df['tm_thread_end'], unit='s')
        df['reply_users'] = df['reply_users'].apply(lambda x: x.split(','))
        df['reply_users_count'] = df['reply_users_count'].astype(int)
        df['reply_count'] = df['reply_count'].astype(int)
        df['msg_dist_type'] = df['msg_dist_type'].apply(lambda x: x.replace('_', ' ').title())
        df['msg_type'] = df['msg_type'].apply(lambda x: x.replace('_', ' ').title())
        df['sender_name'] = df['sender_name'].apply(lambda x: x.replace('_', ' ').title())
        
        
        return df


    #parse slack data from every channel for training 
    @staticmethod
    def slack_parser_all(parent_directory):
        """Parse Slack data from subdirectories to extract information from JSON files."""
        all_data = {
            'msg_type': [], 'msg_content': [], 'sender_name': [],
            'msg_sent_time': [], 'msg_dist_type': [], 'time_thread_start': [],
            'reply_count': [], 'reply_users_count': [], 'reply_users': [],
            'tm_thread_end': [], 'channel': []
        }

        # Traverse through the directory tree starting from the parent directory
        for root, dirs, files in os.walk(parent_directory):
            for file_name in files:
                if file_name.endswith('.json'):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'r', encoding="utf8") as file:
                        try:
                            json_data = json.load(file)

                            if isinstance(json_data, list):  # Assuming each file contains a list of dictionaries
                                for row in json_data:
                                    if isinstance(row, dict):
                                        all_data['msg_type'].append(row.get('type', ''))
                                        all_data['msg_content'].append(row.get('text', ''))
                                        all_data['sender_name'].append(row.get('user_profile', {}).get('real_name', 'Not provided'))
                                        all_data['msg_sent_time'].append(row.get('ts', ''))
                                        if 'blocks' in row and row['blocks']:
                                            block = row['blocks'][0]
                                            if 'elements' in block and block['elements']:
                                                element = block['elements'][0]
                                                if 'elements' in element and element['elements']:
                                                    all_data['msg_dist_type'].append(element['elements'][0].get('type', 'reshared'))
                                                else:
                                                    all_data['msg_dist_type'].append('reshared')
                                            else:
                                                all_data['msg_dist_type'].append('reshared')
                                        else:
                                            all_data['msg_dist_type'].append('reshared')
                                        all_data['time_thread_start'].append(row.get('thread_ts', 0))
                                        all_data['reply_users'].append(",".join(row.get('reply_users', [])))
                                        all_data['reply_count'].append(row.get('reply_count', 0))
                                        all_data['reply_users_count'].append(row.get('reply_users_count', 0))
                                        all_data['tm_thread_end'].append(row.get('latest_reply', 0))
                                        all_data['channel'].append(file_path.split('/')[-2])
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON in file: {file_path}. Error: {e}")

        #create a DataFrame from the extracted data
        df = pd.DataFrame(all_data)
        
        #apply data cleaning and type conversions
        df = df[df['sender_name'] != 'Not provided'].reset_index(drop=True)
        df['msg_sent_time'] = pd.to_datetime(df['msg_sent_time'], unit='s')
        df['time_thread_start'] = pd.to_datetime(df['time_thread_start'], unit='s')
        df['tm_thread_end'] = pd.to_datetime(df['tm_thread_end'], unit='s')
        df['reply_users'] = df['reply_users'].apply(lambda x: x.split(','))
        df['reply_users_count'] = df['reply_users_count'].astype(int)
        df['reply_count'] = df['reply_count'].astype(int)
        df['msg_dist_type'] = df['msg_dist_type'].apply(lambda x: x.replace('_', ' ').title())
        df['msg_type'] = df['msg_type'].apply(lambda x: x.replace('_', ' ').title())
        df['sender_name'] = df['sender_name'].apply(lambda x: x.replace('_', ' ').title())
        
        return df


    @staticmethod
    def parse_slack_reaction(paths):
        combined_data = []

        for path_channel in paths:
            for json_file in glob.glob(f"{path_channel}/*.json"):
                with open(json_file, 'r') as slack_data:
                    data = json.load(slack_data)

                    for item in data:
                        if 'reactions' in item:
                            for reaction in item['reactions']:
                                msg = item.get('text', '')
                                user_id = item.get('user', '')
                                reaction_name = reaction['name']
                                reaction_count = reaction['count']
                                reaction_users = ",".join(reaction['users'])

                                combined_data.append([reaction_name, reaction_count, len(reaction['users']), msg, user_id])

            columns_reaction = ['reaction_name', 'reaction_count', 'reaction_users_count', 'message', 'user_id']
            df_reaction = pd.DataFrame(combined_data, columns=columns_reaction)
            df_reaction['channel'] = [re.search(r'all-week\d', path_channel).group() for _ in range(len(combined_data))]
            return df_reaction


        # for json_file in glob.glob(f"{path}*.json"):
        #     with open(json_file, 'r') as slack_data:
        #         data = json.load(slack_data)

        #         for item in data:
        #             if 'reactions' in item:
        #                 for reaction in item['reactions']:
        #                     msg = item.get('text', '')
        #                     user_id = item.get('user', '')
        #                     reaction_name = reaction['name']
        #                     reaction_count = reaction['count']
        #                     reaction_users = ",".join(reaction['users'])

        #                     #append reaction data to lists

        #                     msg.append(msg)
        #                     user_id.append(user_id)
        #                     reaction_name.append(reaction_name)
        #                     reaction_count.append(reaction_count)
        #                     reaction_users.append(reaction_users)

        # #create a df from collected reaction data
        # reaction_name, reaction_count, reaction_users, msg, user_id = [], [], [], [], []
        # data_reaction = zip(reaction_name, reaction_count, reaction_users, msg, user_id)
        # columns_reaction = ['reaction_name', 'reaction_count', 'reaction_users_count', 'message', 'user_id']
        # df_reaction = pd.DataFrame(data=data_reaction, columns=columns_reaction)
        # df_reaction['channel'] = channel

        
        # return df_reaction

    @staticmethod
    def get_community_participation(path):
        """ specify path to get json files"""
        combined = []
        comm_dict = {}
        for json_file in glob.glob(f"{path}*.json"):
            with open(json_file, 'r') as slack_data:
                combined.append(slack_data)
        # print(f"Total json files is {len(combined)}")
        for i in combined:
            a = json.load(open(i.name, 'r', encoding='utf-8'))

            for msg in a:
                if 'replies' in msg.keys():
                    for i in msg['replies']:
                        comm_dict[i['user']] = comm_dict.get(i['user'], 0)+1
        return comm_dict





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export Slack history')

    
    parser.add_argument('--zip', help="Name of a zip file to import")
    args = parser.parse_args()
