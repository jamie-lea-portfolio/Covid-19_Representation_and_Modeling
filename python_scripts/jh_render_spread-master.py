# Script to generate animations of COVID-19 spread by Jamie Lea
import argparse
import pandas as pd
import numpy as np

import json
import datetime

import shutil
import glob
import os
import errno

import plotly.graph_objects as go
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--feature", choices=["cum_cases", "cum_deaths", "new_cases", "new_deaths"],
                    default="cum_cases")
parser.add_argument("--loc", choices=["USA", "MO_IL"],
                   default="USA")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--debug_timesteps", type=int, default=15)
parser.add_argument("--debug_firststeps", action="store_true")
args = parser.parse_args()

print("!!!Script {}: BEGIN\n".format(parser.prog))
print("Arguments: feature - {}; location - {}; debug - {}\n".format(args.feature, args.loc, args.debug))


# ## Names
master_repo_dir = "/home/happy/deep_learning/covid_graph_model"
resume_repo_dir = "/home/happy/deep_learning/covid_graph_model-resume"
filename_stem = "jh-log_" + args.feature + '-' + args.loc + '_'


# ## Get data
# load the data set and an empty slice
pickle_file = "../model_data/jh_us_timeseries.pkl"
df_jh_timeseries = pd.read_pickle(pickle_file)

empty_counties = "../model_data/jh_us_timeseries-empty_slice.pkl"
df_empty_slice = pd.read_pickle(empty_counties)


# Get the right shape files
if args.loc == "USA":
    counties_file = "../other_data/final_county_borders.20m.geojson"
    states_file = "../other_data/final_state_borders.20m.geojson"
    
elif args.loc == "MO_IL":
    counties_file = "../other_data/final_county_borders-MO_IL.20m.geojson"
    states_file = "../other_data/final_state_borders-MO_IL.20m.geojson"
    

# load the shapes files
counties_shape_dict = None
with open(counties_file, mode='r') as counties_geojson:
    counties_shape_dict = json.load(counties_geojson)
    

states_shape_dict_new = None
with open(states_file, mode="r")  as states_geojson:
    states_shape_dict = json.load(states_geojson)
    
state_codes = pd.read_pickle("../other_data/state_codes.pkl")


# Remove fips not mapped to the 50 states.
state_county_condition = "(subunit_fips > 1000) & (subunit_fips < 60000)"

df_jh_timeseries = df_jh_timeseries.query(state_county_condition)
df_empty_slice = df_empty_slice.query(state_county_condition)


# reset the indexes so that plotly can use them as columns
df_jh_timeseries = df_jh_timeseries.reset_index(level="subunit_fips_str")
df_empty_slice = df_empty_slice.reset_index(level="subunit_fips_str")
state_codes = state_codes.reset_index()


# ### Get the colorbar ceiling for consistent color across timesteps
def get_max_ceil(n):
    print("Maxium value of feature is: ", n)
    log = np.floor(np.log10(n))
    ret_val = 10 ** log
    while ret_val < n:
        ret_val += 10 ** (log - 1)
    print("Maximum value of colorbar is: ", ret_val)
    print("")
    return ret_val


max_ceil = get_max_ceil(df_jh_timeseries[args.feature].max())


# ### Check number of timesteps
print("Number of time steps: {}".format(len(df_jh_timeseries.index.get_level_values(0).unique())))
if args.debug:
    if args.debug_firststeps:
        first_last = "first"
    else:
        first_last = "last"

    print("\tDEBUG MODE: will only render zeroth day + {} {} days".format(first_last, args.debug_timesteps - 1))


# ## Move last anim to old
# ##### If it exists.  The auto regeneration script deletes the image directories after zipping
base_path = os.path.join(master_repo_dir, "images/spread_anim/jh")
date = datetime.datetime.now()
date_stamp = date.strftime("%m-%d-%y")
print("\nThe date is: {}".format(date_stamp))
date_stamp = "gen_" + date_stamp

old_dir_name = filename_stem + "old"
cur_dir_name = filename_stem + "cur"

old_path = os.path.join(base_path, old_dir_name)
cur_path = os.path.join(base_path, cur_dir_name)
print("Removing previous {}".format(cur_dir_name))

try:
    shutil.rmtree(old_path)
except OSError as e:
        if e.errno != errno.ENOENT:
            raise # not a does not exist error      

print("Moving previous current to {}".format(old_dir_name))
try:
    os.rename(cur_path, old_path)
except OSError as e:
        if e.errno != errno.ENOENT:
            raise # not a does not exist error
print("Making new {} directory.  Sub dir is: {}".format(cur_dir_name, date_stamp))
try:
    img_dir = os.path.join(cur_path, date_stamp)
    os.makedirs(img_dir, exist_ok=True)
except OSError as e:
        if e.errno != errno.EEXIST:
            raise # not a directroy exist error.  
            # the directory should have diaappeared in previous step, so we should only get BAD errors
            # but if it still exists, we'll just use it and any remaining images will get overwritten
            

most_recent_date = df_jh_timeseries.index.get_level_values(0).unique()[-1]
most_recent_date = most_recent_date.strftime('%m-%d-%Y')

print("\nMost recent date is: {}\n".format(most_recent_date))


zeroth_date = df_jh_timeseries.index.get_level_values(0).unique()[0] - pd.Timedelta(days=1)
zeroth_date = zeroth_date.strftime('%m-%d-%Y')
cur_date_str = zeroth_date


def write_anim_frame():
    filename = filename_stem + cur_date_str + ".png"
    img_frame = os.path.join(img_dir, filename)
    animation_figure.write_image(img_frame)
    return img_frame


last_image = None

# ## Prepare dataframes
feature_col = None
if args.feature == "cum_cases":
    feature_col = "log_cases"
    feature_type = ("Cumulative", "cases")
    
elif args.feature == "cum_deaths":
    feature_col = "log_deaths"
    feature_type = ("Cumulative", "deaths")
    
elif args.feature == "new_cases":
    feature_col = "log_cases"
    feature_type = ("New", "cases")
    
elif args.feature == "new_deaths":
    feature_col = "log_deaths"
    feature_type = ("New", "deaths")


df_empty_slice = df_empty_slice.reset_index(level=0, drop=True)
df_empty_slice[feature_col] = 0

cur_counties = df_empty_slice


# ## Render animation
jh_github_url = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/"
us_cb_url = "https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html"

data_source_string = "Data from Johns Hopkins University CSSEGIS {} & The US Census Bureau {}".format(
    "", "")


title_suffix = None
if args.loc == "USA":
    title_suffix = " by US County<br>Date: {}" 
elif args.loc == "MO_IL":
    title_suffix = " in MO & IL<br>Date: {}" 
    
base_title_str = feature_type[0] + " COVID-19 " + feature_type[1] + title_suffix

geo_dict = {
    "scope": "usa",
    "visible": False,
}

if args.loc == "MO_IL":
    state_border_thickness = 2
    geo_dict["fitbounds"] = "locations"



titletxt = base_title_str.format(cur_date_str)
layout_var = go.Layout(
    title = {"text": titletxt, "xanchor": "left", "x": 0.03, "y": 0.95, "font":{"size": 32}},
    
    font=dict(
        family="Courier New, monospace",
        size=16,
        color="#7f7f7f"
    ),
    
    width=1920,
    height=1080,
    
    geo=geo_dict,
    
    annotations=[
        go.layout.Annotation(
            text=data_source_string,
            font_size=18,
            align='left',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=-0.0125,
            y=-0.05,
        ),
        go.layout.Annotation(
            text="by Jamie Lea<br>https://github.com/jamie-lea-portfolio/Covid-19_Representation_and_Modeling",
            font_size=18,
            align='right',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=0.9875,
            y=-0.05,
        )
    ],
    margin={"t": 112, "b": 72, "l": 72, "r": 32}
)


# Instantiate figure
animation_figure = go.Figure(layout=layout_var)

# Variables
state_border_thickness = 1.25
    
if feature_type[1] == "cases":
    color_scale = "Darkmint"
elif feature_type[1] == "deaths":
    color_scale = "matter"


tick_vals_list = np.arange(np.log10(max_ceil), dtype=np.int)
tick_text_list = 10 ** tick_vals_list

tick_vals_list = list(tick_vals_list)
tick_vals_list.append(np.log10(max_ceil))

tick_text_list = [str(t) for t in tick_text_list]
tick_text_list.append(max_ceil)


animation_figure.add_choropleth(
    locations=cur_counties['subunit_fips_str'],
    z=cur_counties[feature_col].to_numpy(),
    colorscale=color_scale,
    autocolorscale=False,
    reversescale=False,
    showscale=True,
    geojson=counties_shape_dict,
    colorbar=dict(len=0.75,
                  x=0-0.0125,
                  yanchor='top',
                  y=0.975,
                  tickvals = tick_vals_list,
                  ticktext = tick_text_list,
                  tickfont_size = 20
                 ),
    marker=dict(
            line = dict (
                color = 'black',
                width = 0.15
            )
    ),
    zmin=0, 
    zmid = 0.7, 
    zmax=np.log10(max_ceil)
)


animation_figure.add_choropleth(
    geojson=states_shape_dict,
    locations=state_codes["fips"],
    colorscale=["rgba(0, 0, 0, 0)", "rgba(0, 0, 0, 0)"],
    z=np.ones(52),
    hoverinfo="skip",
    showscale=False,
    marker=dict(
            line = dict (
                color = 'black',
                width = state_border_thickness,
            )
    )
)

# animation_figure.show()
last_image = write_anim_frame()


time_index = df_jh_timeseries.index.get_level_values(0).unique()
if args.debug:
    n = args.debug_timesteps - 1
    if args.debug_firststeps:
        time_index = time_index[:n]
    else:
        time_index = time_index[-n:]


for idx, date in enumerate(time_index):

    cur_date_str = date.strftime('%m-%d-%Y')
    
    cur_data = df_jh_timeseries.loc[date]
    cur_counties.update(df_empty_slice)
    cur_counties.update(cur_data)
    cur_counties[feature_col] = cur_counties[args.feature].apply(lambda x: np.log10(x + 1) if (x != 0) else x)
    
    animation_figure.plotly_restyle(restyle_data={'z': cur_counties[feature_col].to_numpy()}, trace_indexes=0)
    
    
    titletxt = base_title_str.format(cur_date_str)
    animation_figure.update_layout(
        {"title": {"text": titletxt}}
        )

    last_image = write_anim_frame()


print("\nAll images rendered to: \n\t{}\n".format(img_dir))


# ## Organize, animate, save
master_image_dir = os.path.join(master_repo_dir, "images")
resume_image_dir = os.path.join(resume_repo_dir, "images")

if args.debug:
    master_image_dir = os.path.join(master_image_dir, "debug")
    try:
        os.makedirs(master_image_dir, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise # not a directroy exist error.  


# #########################################################################
# names & paths

### REGULAR
# animation
anim_name = filename_stem + "anim.gif"

master_anim_path = os.path.join(master_image_dir, anim_name)
resume_anim_path = os.path.join(resume_image_dir, anim_name)

# last slice
last_slice_name = filename_stem + "most_recent_day.png"
master_last_slice_path = os.path.join(master_image_dir, last_slice_name)
resume_last_slice_path = os.path.join(resume_image_dir, last_slice_name)


# #########################################################################
# glob images
imgs_glob_path = os.path.join(img_dir, filename_stem + "*.png")


# #########################################################################
# remove old images: need to glob since files are date stamped
print("Preparing to remove previous animation and 'most_recent_day' from root images dir")
master_rem_gif = os.path.join(master_image_dir, filename_stem + "*gif")
master_rem_png = os.path.join(master_image_dir, filename_stem + "*png")

resume_rem_gif = os.path.join(resume_image_dir, filename_stem + "*gif")
resume_rem_png = os.path.join(resume_image_dir, filename_stem + "*png")


# images to remove in both resume and master repos
rem_img_glob = []
rem_img_glob.extend([f for f in glob.glob(master_rem_gif)])
rem_img_glob.extend([f for f in glob.glob(master_rem_png)])

if not args.debug:
    rem_img_glob.extend([f for f in glob.glob(resume_rem_gif)])
    rem_img_glob.extend([f for f in glob.glob(resume_rem_png)])
else:
    print("\tDEBUG MODE: skipping removal from resume repo")


print("Removing...")
for f in rem_img_glob:
    if os.path.exists(f):
        os.remove(f)


# #########################################################################
# Animation
### glob pngs for animation
print("\nGlobbing rendered pngs")
pngs = [Image.open(f) for f in sorted(glob.glob(imgs_glob_path))]

### duration
duration_vec = [200] * len(pngs)
duration_vec[-1] = 5000


# #########################################################################
# glob pngs for animation
# #########################################################################
# create basic animation
# code snippet referenced from: https://stackoverflow.com/a/57751793/12316727  
#                                    by https://stackoverflow.com/users/2123555/kris
print("Rendering main animation")
# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
first_frame, *frame_set = pngs
first_frame.save(fp=master_anim_path, format='GIF', append_images=frame_set,
         save_all=True, duration=duration_vec, loop=0)


# ## Copy and link files
# #########################################################################
# last slice
print("Copying main most recent day to master images dir")
shutil.copy(last_image, master_last_slice_path)


# #########################################################################
# create hardlinks in resume repo (unless debug, so as not to break public)
if not args.debug:
    print("\nLinking animations to resume repo:")
    print("Master:")
    os.link(master_anim_path, resume_anim_path)

    # resume
    print("\nLinking last day images to resume repo:")
    print("Master:")
    os.link(master_last_slice_path, resume_last_slice_path)
else:
    print("\tDEBUG MODE: skipping links to resume repo")


# # Script end
print("\n!!!Script {}: ending".format(parser.prog))
