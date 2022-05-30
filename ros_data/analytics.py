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
import heapq
from operator import itemgetter


# dont forget to create 'cache/packages' directory
# loading package DB file
db = MetricDB('packages')
# run python scrap.py before running this file to generate DB

package_list = []
hit_list = []
packages_query = db.query('SELECT url, hits FROM urls WHERE url LIKE "%foxy%"')
packages_data = pd.DataFrame(packages_query)
packages_data = packages_data.reset_index()
packages_data['url'] = packages_data['url'].map(lambda url: re.sub(r'^.*?/ros', '/ros', url))
hit_list = packages_data.loc[:, "hits"].tolist()
raw_urls = (packages_data.loc[:,"url"]).tolist()
print(len(raw_urls))
for i in range(len(raw_urls)):
    package = (''.join(raw_urls[i][:[pos for pos, char in enumerate(raw_urls[i]) if char == '/'][1]+1]))
    package = package.replace("/","")
    package_list.append(package)


# using dictionary comprehension
# to convert package_list, hit_list lists to dictionary
hit_packages_data = {package_list[i]: hit_list[i] for i in range(len(package_list))}


# sort packages upon dowloaded hits
sorted_hit_packages_data = sorted(hit_packages_data.items(), key=lambda val: val[1],reverse= True)[0:10]
#print(sorted_hit_packages_data)

# TODO selecting top 10 packages from pool of exisiting packages
data = heapq.nlargest(10,hit_packages_data.values())
topten_packages = sorted(hit_packages_data.items(), key=itemgetter(1), reverse = True)[0:10]

# for x in sorted_hit_packages_data:  
#   print("{0}: {1}".format(*x))

# converting top ten packages into a dataframe
top_ten_dataframe = pd.DataFrame.from_dict(sorted_hit_packages_data)
top_ten_dataframe.columns = ['packages', 'downloads']
print(top_ten_dataframe)

############# Plot for Overall Distro ratio ####################
packages_overall_data =  { 'Humble' : 635,
 'Galactic' : 41923,
 'Foxy' : 89551,
 'Eloquent Elusor' : 44206,
 'Dashing Diademata' : 69067,
 'Crystal Clemmys' : 25793,
 'Bouncy Bolson' : 11190,
 'Ardent Apalone' : 8150 }

# Data to plot
labels = []
sizes = []

for x, y in packages_overall_data.items():
    labels.append(x)
    sizes.append(y)

# Plot
plt.pie(sizes, labels=labels)

plt.axis('equal')
plt.show()


#############Plot for Top 10 Packages#################

# Draw plot
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(16,10), facecolor='white', dpi= 80)
ax.vlines(x=top_ten_dataframe.index, ymin=0, ymax=top_ten_dataframe.downloads, color='firebrick', alpha=0.7, linewidth=20)

# Annotate Text
for i, downloads in enumerate(top_ten_dataframe.downloads):
    ax.text(i, downloads+0.5, round(downloads, 1), horizontalalignment='center')


# Title, Label, Ticks and Ylim
ax.set_title('Bar Chart for Packages Downloaded', fontdict={'size':22})
ax.set(ylabel='Number of Downloads', ylim=(0, 2000))
plt.xticks(top_ten_dataframe.index, top_ten_dataframe.packages.str.upper(), rotation=30, horizontalalignment='right', fontsize=8)
plt.show()

