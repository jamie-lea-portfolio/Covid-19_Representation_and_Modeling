#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn as sk
import networkx as nx
import datetime
import os
import errno

import plotly.graph_objects as go
import plotly.express as px

import glob
from PIL import Image


# ## Get data

# In[2]:


pickle_file = "../model_data/nyt_county_data_cleaned.pkl"
df_nyt_counties = pd.read_pickle(pickle_file)

empty_counties = "../model_data/nyt_empty_counties_frame_slice.pkl"
df_empty_counties = pd.read_pickle(empty_counties)

counties_shape_dict = None
with open('../other_data/geojson-counties-fips.json', mode='r') as counties_geojson:
    counties_shape_dict = json.load(counties_geojson)


# ### Remove counties not mapped to actual fips
# * nyc
#     * especially remove nyc since it dominates, causing the color map to make the rest of the country look flat
#     * since the county (borough) borders are so small, it doesn't add much to the visualization anyway
# * kc, mo
# * puerto rico, etc.
# * TODO: 
#     * distribute NYC, KC, and Unknown-County-Known-State values across their appropriate counties by population density
#     * double check county fips cross-referencing, figure out why some counties are in black
#         * are they nod in adjacency list?  not in empty county slice?
#         * different lists from the census beaureau in how they handle county equivalent areas (parishes, etc.)

# In[3]:


df_nyt_counties = df_nyt_counties[df_nyt_counties.index.get_level_values(2) > 100]
df_empty_counties = df_empty_counties[df_empty_counties.index.get_level_values(2) > 100]


# ## Get the colorbar ceiling for consistent color across timesteps

# In[4]:


def get_max_ceil(n):
    factor = 10 ** np.floor(np.log10(n))
    result = n // factor
    result += 1
    return result * factor


# In[5]:


max_ceil = get_max_ceil(df_nyt_counties["cases"].max())


# ### Check number of timesteps

# In[6]:


print("Number of time steps: {}".format(len(df_nyt_counties.index.get_level_values(0).unique())))


# In[7]:


most_recent_date = df_nyt_counties.index.get_level_values(0).unique()[-1]
most_recent_date = str(most_recent_date).split()[0]
most_recent_date

mkdir_success = False
ver = 0
while not mkdir_success:
    try:
        img_dir = os.path.join("../images/spread_anim", "upto_" + most_recent_date, "ver_" + str(ver))
        os.makedirs(img_dir)
        mkdir_success = True
    except OSError as e:
            if e.errno != errno.EEXIST:
                raise  # This was not a "directory exist" error.  If directory exists that's ok.
            else:
                ver += 1
print("Date is: {}".format(most_recent_date))
print("Version is: {}".format(str(ver)))
print("Directory is: {}".format(img_dir))


# In[8]:


zeroth_date = df_nyt_counties.index.get_level_values(0).unique()[0] - pd.Timedelta(days=1)
zeroth_date = str(zeroth_date).split()[0]
cur_date_str = zeroth_date


# In[14]:


filename_stem = "log_cum_cases-"
def write_anim_frame():
    filename = filename_stem + cur_date_str + ".png"
    file_path = os.path.join(img_dir, filename)
    log_cases_county_anim.write_image(file_path)  


# In[10]:


cur_counties = df_empty_counties
cur_counties = cur_counties.reset_index("date", drop=True)

cur_counties["log_cases"] = cur_counties["cases"].apply(lambda x: np.log10(x + 1) if (x != 0) else x)

titletxt = "Covid-19 cases by US County {}".format(cur_date_str)
layout = go.Layout(
    title = {"text": titletxt, "xanchor": "left", "x": 0.05, "y": 0.95, "font":{"size": 32}},
    geo_scope='usa', # limit map scope to USA
    font=dict(
        family="Courier New, monospace",
        size=16,
        color="#7f7f7f"
    ),
    width=1920,
    height=1080,
    geo=dict(landcolor = 'black', showlakes=True, lakecolor="#D9E7FF"),
    margin={"t": 96, "b": 48, "l": 0, "r": 32}
)

log_cases_county_anim = go.Figure(layout=layout)
log_cases_county_anim.add_choropleth(
    locations=cur_counties['county_fips_str'],
    z=cur_counties["log_cases"].to_numpy(),
    colorscale=["lightgrey", "red"],
    autocolorscale=False,
    reversescale=False,
    geojson=counties_shape_dict,
    colorbar=dict(len=0.75,
                  x=0.925,
                  tickvals = [0, 1, 2, 3, 4, np.log10(max_ceil)],
                  ticktext = ['0', '10', '100', '1000','10000', max_ceil]
                 ),
    marker=dict(
            line = dict (
                color = 'black',
                width = 0.15
            )
    ),
    zmin=0, zmid = 0.7, zmax=np.log10(max_ceil)
)

write_anim_frame()


# In[17]:


for idx, date in enumerate(df_nyt_counties.index.get_level_values(0).unique()):

    cur_date_str = str(date).split()[0]
    cur_data = df_nyt_counties.loc[date]
    cur_counties.update(cur_data)

    cur_counties["log_cases"] = cur_counties["cases"].apply(lambda x: np.log10(x + 1) if (x != 0) else x)
    log_cases_county_anim.plotly_restyle({'z': cur_counties["log_cases"].to_numpy()})
    
    
    titletxt = "Covid-19 cases by US County {}".format(cur_date_str)
    log_cases_county_anim.update_layout({"title": {"text": titletxt}})

    write_anim_frame()


# In[16]:


# code snippet referenced from: https://stackoverflow.com/a/57751793/12316727  
#                                    by https://stackoverflow.com/users/2123555/kris
# filepaths
imgs_path = os.path.join(img_dir, filename_stem + "*.png")
gif_path = os.path.join(img_dir, "animated.gif")

# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
img, *imgs = [Image.open(f) for f in sorted(glob.glob(imgs_path))]
img.save(fp=gif_path, format='GIF', append_images=imgs,
         save_all=True, duration=200, loop=0)

os.symlink(gif_path, "../images/current_covid_spread-animated.gif")

