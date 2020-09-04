#! /bin/bash
# get plotly orca to work
export DISPLAY=:0

# this script sits in the private repository and is run by a cron job every day at 5:50am CST, it is also occassionally run manually
echo "Regenerating at $(date)"
echo "--------------------------------------"

# #############################################################################
# pull the relevant repositories to 1) get new data and 2) avoid push conflicts
pull_repos() {
	echo "Attempting to pull Johns Hopkins repo" 
	echo "--------------------------------------"
	cd /home/happy/deep_learning/covid_graph_model/johns_hopkins_data && git pull
	echo ""

	echo "Attempting to pull private project repo" 
	echo "--------------------------------------"
	cd /home/happy/deep_learning/covid_graph_model && git pull
	echo ""

	echo "Attempting to pull public resume repo" 
	echo "--------------------------------------"
	cd /home/happy/deep_learning/covid_graph_model-resume && git pull
	echo ""
}
if [ $# -eq 0 ]; then
	pull_repos
elif [ $1 != "--debug" ]; then
	pull_repos
fi
# #############################################################################
# Run scripts

echo "Running python scripts" 
echo "--------------------------------------"
echo "Changing directory to covid_graph_model/python_scripts"
cd /home/happy/deep_learning/covid_graph_model/python_scripts
echo ""

# ###### CLEAN DATA
echo "jh_clean_codemap.py"
echo "--------------------------------"
python3 jh_clean_codemap.py

echo "jh_clean_us_timeseries.py"
echo "--------------------------------"
python3 jh_clean_us_timeseries.py
echo ""

echo "> jh_check_timeseries.py"
echo "--------------------------------"
python3 jh_check_timeseries.py
echo ""

###### RENDER
echo "> jh_render_spread-master.py ::"
echo ""
echo "USA: cum cases"
echo "--------------------------------"
python3 jh_render_spread-master.py --loc="USA" --feature="cum_cases" $1
echo ""

echo "USA: cum deaths"
echo "--------------------------------"
python3 jh_render_spread-master.py --loc="USA" --feature="cum_deaths" $1
echo ""

echo "MO_IL: cum cases"
echo "--------------------------------"
python3 jh_render_spread-master.py --loc="MO_IL" --feature="cum_cases" $1
echo ""

echo "MO_IL: cum deaths"
echo "--------------------------------"
python3 jh_render_spread-master.py --loc="MO_IL" --feature="cum_deaths" $1
echo ""


# #############################################################################
# Resize and optimize .gif's.  This is better than what PIL can do.
cd /home/happy/deep_learning/covid_graph_model/images
for img in *.gif; do
	gifsicle -i $img -O3 --resize 1280x720 -o $img
done


# ###### ZIP EVERYTHING
zip_images() {
	echo "> jh_collect_zips.py"
	echo "--------------------------------"
	python3 jh_collect_zips.py
	echo ""
}

if [ $# -eq 0 ]; then
	zip_images
elif [ $1 != "--debug" ]; then
	zip_images
fi

# #############################################################################
# Now that the source images are zipped we can delete them
remove_images() {
	echo "Removing unneeded images directory covid_graph_model/images/spread_anim/jh"
	cd /home/happy/deep_learning/covid_graph_model/images/spread_anim
	rm -rf "jh"
}
if [ $# -eq 0 ]; then
	remove_images
elif [ $1 != "--debug" ]; then
	remove_images
fi

# #############################################################################
# Update master repo
update_master_repo() {
	echo "Update master repo."
	echo "--------------------------------------"
	echo "Changing directory to root master repo dir: covid_graph_model"
	cd /home/happy/deep_learning/covid_graph_model
	echo "Attempting: git add * && git commit && git push"
	echo ""
	git add * && echo "" && git commit -m "auto update animation" && echo "" && git push && echo "" && echo "Updated master repo at $(date)" >> logs/master_auto_push.log
	echo ""
}
if [ $# -eq 0 ]; then
	update_master_repo
elif [ $1 != "--debug" ]; then
	update_master_repo
fi
# #############################################################################
# Update resume repo
update_resume_repo() {
	echo "Update resume repo"
	echo "--------------------------------------"
	echo "Changing directory to root resume repo dir: covid_graph_model"
	cd /home/happy/deep_learning/covid_graph_model-resume
	echo "Attempting: git add * && git commit && git push"
	echo ""
	git add * && echo "" && git commit -m "auto update animation" && echo "" && git push && echo "" && echo "Updated resume repo at $(date)" >> logs/resume_auto_push.log
	echo ""
}
if [ $# -eq 0 ]; then
	update_resume_repo
elif [ $1 != "--debug" ]; then
	update_resume_repo
fi



echo "Regeneration script finished at $(date)" 
echo "===============================================================================" 
echo "" 
echo "" 
echo ""
