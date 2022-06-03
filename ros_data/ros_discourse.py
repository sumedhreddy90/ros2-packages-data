import pandas as pd
import discourse
import requests

# Data about ROS
searchwords = ['packages', 'package']
tag = "ros2"
URL = "https://discourse.ros.org/tag/" + tag
tables = pd.read_html(URL)
# selecting ROS2 Distro topics data
df = tables[1]
df.head()
df.columns.values.tolist()
df.drop("Unnamed: 1", axis=1, inplace=True)
# print(df)
df['Topic'] = df['Topic'].str.lower()
# search Topic column with search words
# print(' ############Search Results ###########')


# TODO Get Anaytics from Topics depending on Views and Number of Replies
# TODO Sort search results based on replies, views and activity
# TODO get topic ID, Query topic ID to enter into thread and get vaild data

base_url = "https://discourse.ros.org/tag/"
topic_titles = []
topics_data = []
topics_id_data = []

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
    
    if (len(topic_titles) != 0):
        topics_data.extend(topic_titles)
    else:
        print('No data found in ' +  str(page) + ' page')
        break
    
topics_data = pd.DataFrame((topics_data), columns = ['Topics'])
topics_data['Topics'] = topics_data['Topics'].str.lower()
pattern = "packages|\?"
print(topics_data)
print(topics_data[topics_data['Topics'].str.contains('|'.join(searchwords))])

# # Users and their trust levels.s
# api_key_string = "api_key=xxxxxxxxxxxxxx&api_username=sumedh.koppula"
# response = requests.get("https://discourse.ros.org/tag/ros2.json?page=1" + api_key_string)
# users_json = response.json()

# score_data = [[user['username']] for user in users_json if not user['username'] in 
#               ['mark', 'audrey', 'system', 'discobot']]
# print(str(len(score_data)) + " students")
