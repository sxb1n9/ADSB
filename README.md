# ADSB
ADSB Tools and Scripts for PIAWARE, FLIGHTAWARE, ADSBEXCHANGE, RADARBOX

## GAIN_CHECK VERSION 3.2
![Screenshot](https://raw.githubusercontent.com/sxb1n9/ADSB/main/GAIN_CHECK/SCREENSHOTS/gain_check_v3.3.png)
gain_check_v3 will help you determine the correct static gain to use for your ADSB station
```
script_name			= "gain_check_v3.py"
script_version		= "3.3"
script_release		= "RELEASED"
script_author		= "sxb1n9 or b1n9"
print(line_break) #-----------------------------------------------------------------------------------------------------
print("SCRIPT: ", white + script_name + nocolor)
print("VERSION:", white + script_version + space + script_release + nocolor)
print("AUTHOR: ", white + script_author  + nocolor)
print(line_break + white) #---------------------------------------------------------------------------------------------
print("GOAL:" + nocolor)
print("    * script should help you chooose a STATIC GAIN setting that maximizes receiption using more categories")
print("        * ALL MESSAGE TYPES 1-8")
print("            * you also want to maximize type 2 and type 3 messages")
print("        * DISTNACE of RECEPTION including CLOSE, NORMAL, FAR")
print("            * you want to be able to receive (CLS or CLOSE) DISTANCES & FAR_1 or FAR_2 DISTANCES at the same time")
print(line_break + white) #---------------------------------------------------------------------------------------------
print("NOTES:" + nocolor)
print("    * my (b1n9) take and maybe/hopefully an improvement of the optimize_gain.py script by (abcd567)")
print("        * https://discussions.flightaware.com/t/tweaks/20339/36")
print("    * REQUIRES PYTHON 3 for better table display")
print("    * DISTANCES are in MILES")
print("    * DISTANCES are only calculated for TYPE 2 and TYPE 3 MESSAGES with lat/lon positions")
print("    * TYPE 2 GND or SURFACE MESSAGES are counted in 2 categories if they include lat/lon and all TYPE 2")
print("    * TYPE 3 AIR or AIRBORN MESSAGES are counted in 2 categories if they include lat/lon and all TYPE 3")
print(line_break + white) #---------------------------------------------------------------------------------------------
print("RUNNING:" + nocolor)
print("    * I personally run at 5dB steps using short intervals (10s) and do a final verify with a long interval (62s)")
print("        * RUN 1: passes 5, duration 10, gain gain_setp_5")
print("        * RUN 2: passes 5, duration 62, gain gain_setp_5")
print("    * I then run using all gains in the 10-20 dB span around what the first 2 runs tell me to find the best gain")
print("        * RUN 3: passes 5, duration 10, gain gain_all_20")
print("        * RUN 4: passes 5, duration 62, gain gain_all_20")
print(line_break + red) #------------------------------------------------------------------------------------------------
print("WARNING: " + nocolor)
print("    * if script exits before the end it does not reset the original gain and you must do it manually")
print(line_break) #-----------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# PREREQUISITE INSTALLS 
# 	PYTHON 3				sudo apt install python3
# 	PYTHON 3 PIP			sudo apt install python3-pip
# 	BEAUTIFULTABLE			sudo pip3 install beautifultable
# ----------------------------------------------------------------------------------------------------------------------
# INSTALL / UPDATE SCRIPT 
# 	WGET SCRIPT				sudo wget https://github.com/sxb1n9/ADSB/raw/main/GAIN_CHECK/gain_check_v3.py
# ----------------------------------------------------------------------------------------------------------------------
# MODIFY SETTINGS			sudo nano gain_check_v3.py 
# ----------------------------------------------------------------------------------------------------------------------
# REQUIRED GAIN_CHECK SETTINGS DESCRIPTIONS
# 	antenna_lat				location of your antenna for distance calcs in xxx.xxx form) (use at least 3 decimal places for accuracy)
#	antenna_lon				location of your antenna for distance calcs in xxx.xxx form) (use at least 3 decimal places for accuracy)
# 	pass_duration			seconds for each gain (default 62)
# 	pass_number				number of passes to aggregrate for totals (default 5)
# 	gain_choice				variable of gains to use (gains_step_5) or list of gains seperated by space
# ----------------------------------------------------------------------------------------------------------------------
# REQUIRED DUMP1090 SETTINGS DESCRIPTIONS
# 	host 					url of dump1090 (default PIAWARE SD)
# 	port 					30003 = SBS port (default PIAWARE SD)
# 	config_file				path and filename of where gain settings are stored (default PIAWARE SD)
# 	config_setting			gain setting before the gain number
# 								(ex. "rtlsdr-gain 49.6" the config_setting is "rtlsdr-gain" no space after)
# 	config_setting_after	gain setting after the gain number
# 								(ex. "rtlsdr-gain 49.6 something" the config_setting_after is "something" no space before)
# 								(ex. "rtlsdr-gain 49.6" the config_setting_after is "")
# 	service_restart_cmd		command to restart service to apply changed gain (default PIAWARE SD)
# ----------------------------------------------------------------------------------------------------------------------
# OPTIONAL SETTINGS DESCRIPTIONS
#	distance_unit			mile or km (don't change off miles as it doesn't update categories and columns)
#	color_top_percent		5 values in same column within this percentage of the best value will also be highlighted in a different color
# ----------------------------------------------------------------------------------------------------------------------
# RUN 						sudo python3 gain_check_v3.py
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# CHANGELOG
# 3.0
# 	initial
# 3.1
# 	fix distance min
# 	save original value or gain and restore
#	additional starting notes for users
# 	show all 8 types msg count
#		second count for ground and air with lat/lon
# 	added other configs for other setups so that it can be used anywhere
# 	choose distance unit (mile, km)
# 	cleanup and document for release to others
# 	GAIN DESCION MAKING
# 		add top gain per category
# 		add color highlight at end for each column best on the table
# 	keep aircraft distance between all passes
# 	add seconds while receiving gain info
# 3.2
# 	not detecting minimums correctly
# 	not counting distance msgs correctly
# 	updated version and screenshots
# 3.3
# 	add in 2 columns for types 2 and 3 with lat lon
# 	add in pos_ll or positions with LATLON ranking
# 	updated install instructions thanks to (abcd567)
# 	fix issue with categories if set contains no values (issue found by (gavin323))
# 	categories naming updated to be more clear
# 	update script header display
# 	update script final header display to include script_name, script_version, and script_author
# 	remove distance change from miles for now because of all hardcoded categories and columns
# 	update script documentation to be more clear
# 	update formatting to use variables instead of hardcodes
# 	add additional formating
# 	cleanup config line variable naming
# 	fix config_setting and config_setting_after to make it actually work for other than PIAWARE SD
# 	update color display to work with all colors
# 	update to display table with values within color_top_percentage of best value
# ----------------------------------------------------------------------------------------------------------------------
# ISSUES PENDING
# 	fix distance_unit doesn't change category and column ranges
# ----------------------------------------------------------------------------------------------------------------------
# POSSIBLE FUTURE IMPROVEMENTS
# 
# 	EASIER RUNNING IDEA (b1n9)
# 		argument passing so you don't need to edit file
# 		exit cleanly button combo besides cntl C
# 
# 	INCLUDE RSSI (not included on 30003) (b1n9)
# 		count < -3db signals if we can get rssi
# 		rssi sections like distance
# 		rssi min max
# 
# 	RANKING & COLORING IMPROVEMENT IDEA (b1n9)
#		best        teal    +2
#		top 5%      blue    +1
#		middle		norm	0
# 		bottom 5%   pink    -1
# 		worst       red     -2
# 		settings for ranking top and bottom percentages
# 		display gain ranking numbers 
#		display colored table and ranking at end of each pass and don't clear right away
# ----------------------------------------------------------------------------------------------------------------------
```



## STATSV2
updates to graphs1090 and hub for multisites on piaware

# NOTES
## LOCATIONS
## DEBUG
