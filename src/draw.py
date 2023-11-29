import datetime
import glob
import json
import os
import re
import sys
from collections import Counter

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from nltk.corpus import stopwords
from wordcloud import WordCloud


class Visualize():
    '''
    Wrapper class to visualize the data
    
    The notebook got so congested with all the visualization code.
    So I decided to move them to a separate class.
    
    Below are the functions used to draw the visualizations.
    
    '''

    def __init__(self, data):
        self.data = data
        self.users = data.users
        self.channels = data.channels
        self.messages = data.mess


    @staticmethod
    def get_top_20_user(data, channel='Random'):
        """get user with the highest number of message sent to any channel"""

        data['sender_name'].value_counts()[:20].plot.bar(figsize=(15, 7.5))
        plt.title(f'Top 20 Message Senders in #{channel} channels', size=15, fontweight='bold')
        plt.xlabel("Sender Name", size=18); plt.ylabel("Frequency", size=14);
        plt.xticks(size=12); plt.yticks(size=12);
        plt.show()

        data['sender_name'].value_counts()[-10:].plot.bar(figsize=(15, 7.5))
        plt.title(f'Bottom 10 Message Senders in #{channel} channels', size=15, fontweight='bold')
        plt.xlabel("Sender Name", size=18); plt.ylabel("Frequency", size=14);
        plt.xticks(size=12); plt.yticks(size=12);
        plt.show()

    def draw_avg_reply_count(data, channel='Random'):
        """who commands many reply?"""

        data.groupby('sender_name')['reply_count'].mean().sort_values(ascending=False)[:20]\
            .plot(kind='bar', figsize=(15,7.5));
        plt.title(f'Average Number of reply count per Sender in #{channel}', size=20, fontweight='bold')
        plt.xlabel("Sender Name", size=18); plt.ylabel("Frequency", size=18);
        plt.xticks(size=14); plt.yticks(size=14);
        plt.show()

    def draw_avg_reply_users_count(data, channel='Random'):
        """who commands many user reply?"""

        data.groupby('sender_name')['reply_users_count'].mean().sort_values(ascending=False)[:20].plot(kind='bar',
        figsize=(15,7.5));
        plt.title(f'Average Number of reply user count per Sender in #{channel}', size=20, fontweight='bold')
        plt.xlabel("Sender Name", size=18); plt.ylabel("Frequency", size=18);
        plt.xticks(size=14); plt.yticks(size=14);
        plt.show()

    def draw_wordcloud(msg_content, week):    
        # word cloud visualization
        allWords = ' '.join([twts for twts in msg_content])
        wordCloud = WordCloud(background_color='#975429', width=500, height=300, random_state=21, max_words=500, mode='RGBA',
                                max_font_size=140, stopwords=stopwords.words('english')).generate(allWords)
        plt.figure(figsize=(15, 7.5))
        plt.imshow(wordCloud, interpolation="bilinear")
        plt.axis('off')
        plt.tight_layout()
        plt.title(f'WordCloud for {week}', size=30)
        plt.show()

    def draw_user_reaction(data, channel='General'):
        data.groupby('sender_name')[['reply_count', 'reply_users_count']].sum()\
            .sort_values(by='reply_count',ascending=False)[:10].plot(kind='bar', figsize=(10, 5))
        plt.title(f'User with the most reaction in #{channel}', size=25);
        plt.xlabel("Sender Name", size=18); plt.ylabel("Frequency", size=18);
        plt.xticks(size=14); plt.yticks(size=14);
        plt.show()



