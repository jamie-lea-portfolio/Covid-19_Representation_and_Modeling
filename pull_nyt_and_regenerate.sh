#! /bin/bash
# this script sits in the private repository and is run by a cron job every day at 5:50am CST, it is also occassionally run manually
time_stamp=$(date)
echo "Script started at $time_stamp\n" >> /tmp/debug_cron
# get plotly orca to work
export DISPLAY=:0
cd /home/happy/deep_learning/covid_graph_model/nyt_repo && git pull
cd /home/happy/deep_learning/covid_graph_model/python_scripts
python3 clean_nyt_county_data.py
python3 nytimes_render_spread-optimize.py
cd /home/happy/deep_learning/covid_graph_model-resume/images
rm current_covid_spread-animated.gif
ln /home/happy/deep_learning/covid_graph_model/images/current_covid_spread-animated.gif
cd /home/happy/deep_learning/covid_graph_model-resume
git pull
time_stamp=$(date)
echo "updating at $time_stamp\n" >> auto_update.log
git add *
git commit -m "auto update animation"
git push
time_stamp=$(date)
echo "Script finished at $time_stamp\n" >> /tmp/debug_cron