#! /bin/bash
# this script sits in the private repository and is run by a cron job every day at 5:50am CST, it is also occassionally run manually
# get plotly orca to work
export DISPLAY=:0
# pull the relevant repositories to 1) get new data and 2) avoid push conflicts
cd /home/happy/deep_learning/covid_graph_model/nyt_repo && git pull
cd /home/happy/deep_learning/covid_graph_model && git pull
cd /home/happy/deep_learning/covid_graph_model-resume && git pull

# regenate the cleaned data (can't iteratively update since NYTimes might overwrite old data with new info)
cd /home/happy/deep_learning/covid_graph_model/python_scripts
python3 clean_nyt_county_data.py
python3 nytimes_render_spread-optimize.py

# go to resume version , remove old hardlink and create new one
cd /home/happy/deep_learning/covid_graph_model-resume/images
rm current_covid_spread-animated.gif
ln /home/happy/deep_learning/covid_graph_model/images/current_covid_spread-animated.gif
ln /home/happy/deep_learning/covid_graph_model/images/most_recent_day.gif

# get timestamp to update the auto-update log
cd /home/happy/deep_learning/covid_graph_model-resume && git pull
time_stamp=$(date)
echo "updating at resume repo at $time_stamp\n" >> auto_update.log
git add *
git commit -m "auto update animation"
git push
