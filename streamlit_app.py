#create a dashboard with streamlit for sentiment analysis

from gc import collect
from operator import index

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
from click import style
from pick import Picker
from pymongo import MongoClient
from pyparsing import col

################### PAGE SETUP ######################
# Create a title and sub-title
st.set_page_config(page_title="Ten EDA", page_icon=":sunglasses:", layout='wide')
st.title(" :bar_chart: Ten Academy EDA Dashboard")
# st.markdown('<style>div.block-container{background-color: #f9f9f9;}</style>', unsafe_allow_html=True)
f1 = st.file_uploader(":file_folder: Upload your file", type=['csv', 'xlsx'])

# if f1 is not None:
#     filename = f1.name
#     st.success(f'File "{filename}" successfully uploaded')
#     st.write(filename)
#     dif = pd.read_csv(filename, encoding="ISO-8859-1")
# else:
#     st.warning('Please upload a file')
#     st.stop()


#columns 
col1, col2 = st.columns((2))




###################################################

client = MongoClient("mongodb://localhost:27017/")

db = client['tenacademy']
collection = db['10academy']
collection2 = db['sentimentdata']

#Entire Data
cursor = collection.find()
df = pd.DataFrame(list(cursor))


#Sentiment Data
sentiment = collection2.find()
sent = pd.DataFrame(list(sentiment))

##################################################

# sns.set_style("darkgrid")
# sns.set_context("paper", font_scale=1.5, rc={"lines.linewidth": 2.5})

reply_counts = df.groupby('sender_name')['reply_count'].sum().sort_values(ascending=False)

top_senders = pd.DataFrame({
    'Sender Name': reply_counts[:10].index,
    'Reply Count': reply_counts[:10].values
})
with col1:
    st.subheader('Top 10 users with the highest reply count')
    st.bar_chart(top_senders.set_index('Sender Name'))



user_msg_counts = df['sender_name'].value_counts()
user_msg_counts_df = pd.DataFrame({'sender_name': user_msg_counts[:10].index, 'msg_count': user_msg_counts[:10].values})

with col2:
    st.subheader('Top 10 users with the highest message count')
    st.scatter_chart(user_msg_counts_df.set_index('sender_name'), height=500, width=100, use_container_width=True)


# with col1:
#     st.subheader(" :gear: Top 10 Senders by Pie")
#     fig = px.pie(user_msg_counts_df, hole=0.5)
#     st.plotly_chart(fig)

    
user_message_counts = df.groupby('sender_name').size()

top_10_users = user_message_counts.nlargest(10)

user_message_counts_df = pd.DataFrame({'message_count': top_10_users.values}, index=top_10_users.index)
with col1:
   st.subheader("Big time message writers")
   st.bar_chart(user_message_counts_df, color=["#ffaa00"]) 



# Convert 'msg_sent_time' column to datetime format
df['msg_sent_time'] = pd.to_datetime(df['msg_sent_time'], infer_datetime_format=True)

# Extract hour from message timestamps
df['hour_sent'] = df['msg_sent_time'].dt.hour

# Group messages by hour and count the number of messages in each hour
hourly_message_count = df.groupby('hour_sent').size()


hour_peak = hourly_message_count.idxmax()
max_messages = hourly_message_count.max()

with col2:
    st.subheader('Hourly messages sent')
    st.line_chart(hourly_message_count, width=200, height=200)
    st.write(f"The peak hour with the highest number of messages is hour {hour_peak} with {max_messages} messages.")



st.subheader("Time Series on Sentiment Analysis")

sentiment_data = pd.DataFrame({
    'Negative': sent['negative'],
    'Neutral': sent['neutral'],
    'Positive': sent['positive']
})




sentiment_type = st.sidebar.selectbox("Select Sentiment", ["Negative", "Neutral", "Positive"])
st.subheader(f" :sob: :joy: :neutral_face: Time Series chart for {sentiment_type} sentiment over time")
st.line_chart(sentiment_data[sentiment_type],use_container_width=True)


# st.write(df)