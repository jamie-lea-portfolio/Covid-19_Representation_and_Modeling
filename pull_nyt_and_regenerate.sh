#! /bin/bash
# this script sits in the private repository and is run by a cron job every day at 5:50am CST, it is also occassionally run manually
time_stamp=$(date)
echo "Regenerating at $time_stamp" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
echo "--------------------------------------" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
# get plotly orca to work
export DISPLAY=:0
# pull the relevant repositories to 1) get new data and 2) avoid push conflicts
# echo "Attempting to pull NYTimes repo" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
# cd /home/happy/deep_learning/covid_graph_model/nyt_repo && git pull

echo "Attempting to pull Johns Hopkins repo" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
cd /home/happy/deep_learning/covid_graph_model/johns_hopkins_data && git pull

echo "Attempting to pull private project repo" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
cd /home/happy/deep_learning/covid_graph_model && git pull

echo "Attempting to pull public resume repo" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
cd /home/happy/deep_learning/covid_graph_model-resume && git pull

# regenate the cleaned data (can't iteratively update since NYTimes might overwrite old data with new info)
echo "Running python scripts" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
cd /home/happy/deep_learning/covid_graph_model/python_scripts
python3 jh_clean_us_timeseries.py
python3 jh_check_timeseries.py
python3 jh_render_spread-cum_cases.py
python3 jh_render_spread-cum_deaths.py

echo "Attempting to add & commit & push resume repo" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
echo "Updating resume repo at $time_stamp" >> master_auto_update.log

# go to resume version , remove old hardlink and create new one.  Have to be hardlinks for github to pull
echo "Creating image hardlinks to resume repo" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
cd /home/happy/deep_learning/covid_graph_model-resume/images
# Update cases
rm jh-cum_cases-animated.gif
ln /home/happy/deep_learning/covid_graph_model/images/jh-cum_cases-animated.gif
rm jh-cum_cases-most_recent_day.png
ln /home/happy/deep_learning/covid_graph_model/images/most_recent_day.png

# Update deaths
rm jh-cum_deaths-animated.gif
ln /home/happy/deep_learning/covid_graph_model/images/jh-cum_deaths-animated.gif 
rm jh-cum_deaths-most_recent_day.png
ln /home/happy/deep_learning/covid_graph_model/images/jh-cum_deaths-most_recent_day.png

# get timestamp to update the auto-update log
echo "Attempting to add & commit & push resume repo" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
echo "Updating resume repo at $time_stamp" >> resume_auto_update.log
git add * && git commit -m "auto update animation" && git push

echo "Regeneration script end" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
echo "--------------------------------------" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
echo "" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
echo "" >> /home/happy/deep_learning/covid_graph_model/logs/regen.log
