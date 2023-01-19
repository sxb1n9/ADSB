

print("--------------------------------------------------------------------------------")
print(blue + "SCRIPT  gain_check_v3.py" + nocolor)
print(blue + "VERSION 3.1" + nocolor)
print(blue + "AUTHOR  b1n9" + nocolor)
print("--------------------------------------------------------------------------------")
print("goal of this tool is to help you chooose a static gain setting that maximizes")
print("messages with position and distance of receiption at the same time")
print("you want to be able to read CLS or close and FAR_1 and FAR_2 at the same time")
print("you also want to maximize type 2 and type 3 messages")
print("--------------------------------------------------------------------------------")
print("distances are in miles")
print("distances are only calculated for type 2 and type 3 messages with lat/lon")
print("type 2 gnd or surface messages are counted if they include lat/lon or not")
print("type 3 air or airborn messages are counted if they include lat/lon or not")
print("--------------------------------------------------------------------------------")
# ----------------------------------------------------------------------------------------------------------------------
# NOTES:
# 	unfortunatly requires python 3 for better table display
# 	my (b1n9) take and maybe an improvement of the optimize gain script by (abcd567)
# 		https://discussions.flightaware.com/t/tweaks/20339/36
# ----------------------------------------------------------------------------------------------------------------------
# WARNING: 	if script exits before the end it does not reset the original gain
# ----------------------------------------------------------------------------------------------------------------------
# 3.0
# 	initial
# 3.1 (pending)
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
# 	keep aircraft distance between all passes (started distances array but not finished)
# 	add seconds while receiving gain info
# ----------------------------------------------------------------------------------------------------------------------
# POSSIBLE FUTURE IMPROVEMENTS
# 	SCRIPT CONTROL
# 		argument passing so you don't need to edit file
# 		exit cleanly button combo besides cntl C
# 	DATA
# 		save directly to results variable instead of using intermediate variables 
# 	RSSI (not included on 30003)
# 		count < -3db signals if we can get rssi
# 		rssi sections like distance
# 		rssi min max
# ----------------------------------------------------------------------------------------------------------------------
# I personally run this in 5 passes with 10s durations first then verify with another run of 5 passes of 62s intervals
# 	RUN 1: passes 5, duration 10, gain gain_setp_5
# 	RUN 2: passes 5, duration 62, gain gain_setp_5
# 	RUN 3: passes 5, duration 62, gain gain_all_20
# ----------------------------------------------------------------------------------------------------------------------
# REQUIRED INSTALLS 
# 	PYTHON 3.9 or 3.10 		sudo apt install python3.10
# 	BEAUTIFULTABLES:		sudo pip3 install beautifultables
# ----------------------------------------------------------------------------------------------------------------------
# REQUIRED SETTING DESCRIPTIONS
# 	antenna_lat 			location of your antenna for distance calcs in xxx.xxx form) (use at least 3 decimal places for accuracy)
#	antenna_lon 			location of your antenna for distance calcs in xxx.xxx form) (use at least 3 decimal places for accuracy)
# 	pass_duration 			seconds for each gain (default 62)
# 	pass_number 			number of passes to aggregrate for totals (default 5)
# 	gain_choice 			variable of gains to use (gains_step_5) or list of gains seperated by space
#
#	distance_unit			mile or km
#
# 	host 					url of dump1090 (default PIAWARE SD)
# 	port 					30003 = SBS port (default PIAWARE SD)
# 	config_file				path and filename of where gain settings are stored (default PIAWARE SD)
# 	config_name				name of gain setting to change (default PIAWARE SD)
# 	service_restart_cmd		command to restart service to apply changed gain (default PIAWARE SD)
# ----------------------------------------------------------------------------------------------------------------------
# MODIFY SETTINGS			sudo nano gain_check_v3.py 
# RUN 						sudo python3 gain_check_v3.py
# ----------------------------------------------------------------------------------------------------------------------

# GAIN SETTINGS (DON'T CHANGE)
gains_step_5		= "12.5 15.7 20.7 25.4 29.7 36.4 40.2 44.5 49.6"
gains_step_10 		= "12.5 20.7 29.7 40.2 49.6"

gains_40_50			= "40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_30_40			= "29.7 32.8 33.8 36.4 37.2 38.6 40.2"
gains_20_30			= "20.7 22.9 25.4 28.0 29.7"
gains_10_20 		= "12.5 14.4 15.7 16.6 19.7 20.7"
gains_00_10 		= "0.0 0.9 1.4 2.7 3.7 7.7 8.7 12.5"

gains_all_40 		= "40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_all_30 		= "29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_all_20 		= "20.7 22.9 25.4 28.0 29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_all_10		= "12.5 14.4 15.7 16.6 19.7 20.7 22.9 25.4 28.0 29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_all_00		= "0.0 0.9 1.4 2.7 3.7 7.7 8.7 12.5 14.4 15.7 16.6 19.7 20.7 22.9 25.4 28.0 29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6"

# REQUIRED SETTING
antenna_lat			= 33.444
antenna_lon			= -112.069
pass_duration		= 10
pass_number			= 5
gain_choice			= gains_step_5

distance_unit		= 'mile'

# PIAWARE SD SETTINGS (comment out and uncomment other settings to switch)
host				= 'localhost'
port 				= 30003
config_file			= '/boot/piaware-config.txt'
config_name			= 'rtlsdr-gain'
config_setting		= 'rtlsdr-gain '
config_setting_2	= ''
service_restart_cmd	= 'sudo systemctl restart dump1090-fa'

# DUMP1090-FA on RASPBIAN
# host					= 'localhost'
# port 					= 30003
# config_file			= '/etc/default/dump1090-fa'
# config_name			= 'RECEIVER_OPTIONS'
# config_setting		= 'RECEIVER_OPTIONS="--device-index 0 --ppm 0 --gain '
# config_setting_2		= ' --net-bo-port 30005 --net-sbs-port 30003'
# service_restart_cmd	= 'sudo systemctl restart dump1090-fa'

# DUMP1090-MUTABILITY on RASPBIAN
# host					= 'localhost'
# port 					= 30003
# config_file			= '/etc/default/dump1090-mutability'
# config_name			= 'GAIN'
# config_setting		= 'GAIN='
# config_setting_2		= ''
# service_restart_cmd	= 'sudo systemctl restart dump1090-mutability'