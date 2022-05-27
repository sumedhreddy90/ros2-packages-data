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
# run python scrap.py before running this file to generate DB
db = MetricDB('packages')

# processing packages data

package_list = []
packages_query = db.query('SELECT url, hits FROM urls WHERE url LIKE "%galactic%"')
packages_data = pd.DataFrame(packages_query)
packages_data = packages_data.reset_index()
packages_data['url'] = packages_data['url'].map(lambda url: re.sub(r'^.*?/ros', '/ros', url))
raw_urls = (packages_data.loc[:15,"url"]).tolist()
print(len(raw_urls))
for i in range(len(raw_urls)):
    package = (''.join(raw_urls[i][:[pos for pos, char in enumerate(raw_urls[i]) if char == '/'][1]+1]))
    package = package.replace("/","")
    package_list.append(package)

print(package_list)

# TODO sort packages upon dowloaded hits