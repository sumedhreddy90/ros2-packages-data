import pandas as pd
import pandas as pd

#Data about ROS

tag = "ros2"
URL = "https://discourse.ros.org/tag/" + tag
tables = pd.read_html(URL)
# selecting ROS2 Distro topics data
df = tables[1]
df.head()
df.columns.values.tolist()
df.drop("Unnamed: 1", axis=1, inplace=True)
print(df)

#TODO Get Anaytics from Topics depending on Views and Number of Replies