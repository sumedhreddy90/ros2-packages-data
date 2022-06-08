""" 
Copyright (c) 2022 Sumedh Koppula and Open Robotics

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
""" 

from itertools import count
from urllib import response
import pandas as pd
import discourse
from pexpect import ExceptionPexpect
import config
import requests
import asyncio
import aiohttp
from collections import Counter
from nltk.corpus import stopwords
import nltk 
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

url = 'https://discourse.ros.org/'
topic_title = []
package_topics_tokens = []
topics_token = []
post_ids = []
package_topics_Ids = []
searchwords = ['packages', 'package']
tag = "ros2"

def discourseAPIData():

    global client
    client = discourse.Client(
        host= config.api_url,
        api_username= config.api_user,
        api_key= config.api_key,
    )
    return client

def get_tasks(session, Ids):
    tasks = []
    for id in Ids:
        tasks.append(session.get(url + 't/{}.json?'.format(id) + config.api_key_string))
    return tasks
         
async def getPostIDs(Ids):
    try:
        async with aiohttp.ClientSession() as session:
            tasks = get_tasks(session, Ids)
            responses = await asyncio.gather(*tasks)
            for resp in responses:
                resp.json()
                posts = resp['posts']
                for id in posts:
                    post_ids.append(id['id'])

        return post_ids
   
    except Exception as e :
        print("error:",e)

def tokenizer(sorted_topics):
    text_tokens = word_tokenize(sorted_topics)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]

    return tokens_without_sw

def plotter(tokens_without_sw):
    letter_counts = Counter(tokens_without_sw)
    df = pd.DataFrame.from_dict(letter_counts, orient='index')
    df.plot(kind='bar')
     

def main():
    topics_data = []
    topics_ids = []
    client =  discourseAPIData()
    latest = client.get_latest_topics('default')
    

    
    base_url = "https://discourse.ros.org/tag/"

    for page in range(100):
        url_template = base_url + tag + ".json?page=" + str(page)
        response = requests.get(url_template)
        response_json = response.json()
        topic_titles = [topic['title'] for topic in response_json['topic_list']['topics']]
        topic_tags = [topic['tags'] for topic in response_json['topic_list']['topics']]
        topic_id = [topic['id'] for topic in response_json['topic_list']['topics']]
        topic_views = [topic['views'] for topic in response_json['topic_list']['topics']]
        topic_likes = [topic['like_count'] for topic in response_json['topic_list']['topics']]
        topic_has_answer = [topic['has_accepted_answer'] for topic in response_json['topic_list']['topics']]

        if (len(topic_titles) and len(topic_id) != 0):
            topics_data.extend(topic_titles)
            topics_ids.extend(topic_id)
        else:
            print('No data found in ' +  str(page) + ' page')
            break



    data = {'Topics':topics_data,'Topic Ids':topics_ids}
    topics_data_df = pd.DataFrame(data)
    topics_data_df['Topics'] = topics_data_df['Topics'].str.lower()
    package_df = (topics_data_df[topics_data_df['Topics'].str.contains('|'.join(searchwords))])
    package_topics_data = package_df['Topics'].tolist()
    package_topics_Ids = package_df['Topic Ids'].tolist()

    # Tokenize all topics with tag: ros2
    for topic in topics_data:
      topics_token.extend(tokenizer(topic))
    # Tokenize topics with tag and search words
    for topic_package in package_topics_data:
      package_topics_tokens.extend(tokenizer(topic_package))
    
    # for tid in package_topics_Ids:
    #     post_data = client.get_topic(tid)
    #     post_ids.extend(getPostIDs(post_data))
    # print(len(post_ids))
    # plotter(topics_token)
  
    asyncio.run(getPostIDs(package_topics_Ids))
    
if __name__ == "__main__":
   (main())