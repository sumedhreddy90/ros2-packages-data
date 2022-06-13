from multiprocessing.connection import wait
import aiohttp
import asyncio
import config
import time
import json
import re
import requests
import pandas as pd
import discourse
from types import SimpleNamespace
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from collections import Counter
import matplotlib.pyplot as plt


tag = "ros2"
searchwords = ['packages', 'package']
package_topics_tokens = []
topics_token = []
cooked_data = []
cooked_tokens = []
CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

client = discourse.Client(
        host= config.api_url,
        api_username= config.api_user,
        api_key= config.api_key,
    )
f = open("post_data.txt", "w")


async def fetch(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            response.raise_for_status()
        return await response.text()

def tokenizer(sorted_topics):
    text_tokens = word_tokenize(sorted_topics)
    # removing stop words from NLTK
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
    # Removing top 1000 common word
    text_file = open("ros_data/common_words.txt", "r")
    common_words = text_file.read().split(',')
    tokens_without_sw = [word for word in tokens_without_sw if not word in common_words]
    tokens = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in tokens_without_sw]
   
    return tokens

def plotter(tokens_without_sw):
    df = pd.DataFrame(tokens_without_sw, columns = ['Topic words'])
    top_N = 55
    a = df['Topic words'].str.lower().str.cat(sep=' ')
    words = nltk.tokenize.word_tokenize(a)
    word_dist = nltk.FreqDist(words)
    rslt = pd.DataFrame(word_dist.most_common(top_N),
                        columns=['Topic_Words', 'Frequency'])
    unwanted = ['ros', '', 'i', '2', 'meeting', 'group', 'new', 'engineer','c', 'nan','ros1','2019','hiring', 'may','online','remote','software', '2021', 'using', 'wg', 'working', 'package', 'robot', 'support', '2020', 'call', 'open', 'new', 'announcing', 'how', '2022', 'looking', 
    'development', 'would', 'the', 'list', 'like', 'make', 'use', 'thanks', 'think', 'if']
    for w in unwanted:
        rslt = rslt[rslt.Topic_Words != str(w)]

    rslt.plot(x="Topic_Words", y=["Frequency"], kind="bar", title="ROS Discourse ROS2 tagged topics data", figsize=(9, 8))    
    plt.show( )
    print(rslt)

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', str(raw_html))
  return cleantext

async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        await asyncio.sleep(5)
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def getData(flag, Idx):
    # Get Cooked data for each post for associated topics
    async with aiohttp.ClientSession() as session:
        
        url = 'https://discourse.ros.org/'
        post_ids = []
        post_urls = []
        topic_urls = []
        if(flag == 'get_post_id'):
            for id in Idx:
                resp_topics = url + 't/{}.json?'.format(id) + config.api_key_string
                topic_urls.append(resp_topics)

            responses_topics = await fetch_all(session, topic_urls)
            for resp in responses_topics:
                data_t = json.loads(resp, object_hook=lambda d: SimpleNamespace(**d))
                posts = data_t.post_stream.posts
                for post_id in posts:
                    post_ids.append(post_id.id)
            
            return post_ids

        else:
            for id in Idx:
                resp = url + '/posts/' + '{}.json?'.format(id) + config.api_key_string
                post_urls.append(resp)
        
            responses = await fetch_all(session, post_urls)
            for resp in responses:
                data = json.loads(resp, object_hook=lambda d: SimpleNamespace(**d))
                if (data.cooked is not None):
                    cooked = data.cooked
                    # regex to extract required strings
                    reg_str = "<" + "p" + ">(.*?)</" + "p" + ">"
                    res = re.findall(reg_str, cooked)
                    cleaned_text = cleanhtml(res)
                    f.write(''.join(str(cleaned_text)))
                    cooked_data.append(cleaned_text)
                else:
                    print('Post does not have cooked data')
            return cooked_data

async def main():
    topics_data = []
    topics_ids = [] 
    base_url = "https://discourse.ros.org/tag/"

    for page in range(100):
        url_template = base_url + tag + ".json?page=" + str(page)
        response = requests.get(url_template)
        response_json = response.json()
        topic_titles = [topic['title'] for topic in response_json['topic_list']['topics']]
        topic_id = [topic['id'] for topic in response_json['topic_list']['topics']]
        
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
    

    #Histogram topic words
    plotter(topics_token)   
    
    #Get Post Ids for associated topic Ids
    post_ids = await getData('get_post_id', package_topics_Ids)
    
    #Get Cooked Post data from each Post Id
    cooked_data = await getData('get_cooked',post_ids)
    for cook in cooked_data:
        cooked_tokens.extend(tokenizer(cook))
    
    #Histogram Post words wrt each topic
    plotter(cooked_tokens)   
    f.close()
        

if __name__ == '__main__':
    asyncio.run(main())
