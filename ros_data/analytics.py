import string
import re
import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
import readability as rd
from bs4 import BeautifulSoup
from metric_db import MetricDB
from collections import Counter
import wordcloud

# dont forget to create 'cache/packages' directory
# loading package DB file
db = MetricDB('packages')
# run python scrap.py before running this file to generate DB

package_list = []
hit_list = []
packages_query = db.query('SELECT url, hits FROM urls WHERE url LIKE "%galactic%"')
packages_data = pd.DataFrame(packages_query)
packages_data = packages_data.reset_index()
packages_data['url'] = packages_data['url'].map(lambda url: re.sub(r'^.*?/ros', '/ros', url))
hit_list = packages_data.loc[:15, "hits"].tolist()
raw_urls = (packages_data.loc[:15,"url"]).tolist()

for i in range(len(raw_urls)):
    package = (''.join(raw_urls[i][:[pos for pos, char in enumerate(raw_urls[i]) if char == '/'][1]+1]))
    package = package.replace("/","")
    package_list.append(package)


# using dictionary comprehension
# to convert package_list, hit_list lists to dictionary
hit_packages_data = {package_list[i]: hit_list[i] for i in range(len(package_list))}
print(hit_packages_data)

# TODO sort packages upon dowloaded hits