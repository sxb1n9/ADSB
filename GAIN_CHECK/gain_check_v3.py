#!/usr/bin/python3
import time, socket, subprocess, fileinput, os
from math import sin, cos, sqrt, atan2, radians
from beautifultable import BeautifulTable

# SEE BELOW LINE 50+ FOR INSTRUCTIONS

# FORMATS
space				= " "
tab					= "\t"
newline				= "\n"
clear 				= chr(27) + "[2J"
line_break			= "------------------------------------------------------------------------------------------------------------------------"
line_dotted			= "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - "

# COLORS
color_esc 			= "\033["
color_break			= ";"
color_end_m			= "m"

color_normal 		= "0"
color_bright		= "1"
color_underline		= "2"
color_negative_1	= "3"
color_negative_2 	= "5"

color_foreground	= "3"
color_background	= "4"

color_grey			= "0"
color_red			= "1"
color_green			= "2"
color_yellow		= "3"
color_blue			= "4"
color_pink			= "5"
color_cyan			= "6"
color_white			= "7"
color_black			= "8"

grey				= color_esc + color_bright + color_break + color_foreground + color_grey   + color_break + color_background + color_black + color_end_m
red 				= color_esc + color_bright + color_break + color_foreground + color_red    + color_break + color_background + color_black + color_end_m
green 				= color_esc + color_bright + color_break + color_foreground + color_green  + color_break + color_background + color_black + color_end_m
yellow 				= color_esc + color_bright + color_break + color_foreground + color_yellow + color_break + color_background + color_black + color_end_m
blue 				= color_esc + color_bright + color_break + color_foreground + color_blue   + color_break + color_background + color_black + color_end_m
pink 				= color_esc + color_bright + color_break + color_foreground + color_pink   + color_break + color_background + color_black + color_end_m
cyan 				= color_esc + color_bright + color_break + color_foreground + color_cyan   + color_break + color_background + color_black + color_end_m
white 				= color_esc + color_bright + color_break + color_foreground + color_white  + color_break + color_background + color_black + color_end_m
black 				= color_esc + color_bright + color_break + color_foreground + color_black  + color_break + color_background + color_black + color_end_m
nocolor 			= color_esc + color_grey + color_end_m

# HEADER
print(clear)
print(nocolor)
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

# GAIN SETTINGS (DON'T CHANGE)
gains_step_5			= "12.5 15.7 20.7 25.4 29.7 36.4 40.2 44.5 49.6"
gains_step_10 			= "12.5 20.7 29.7 40.2 49.6"

gains_40_50				= "40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_30_40				= "29.7 32.8 33.8 36.4 37.2 38.6 40.2"
gains_20_30				= "20.7 22.9 25.4 28.0 29.7"
gains_10_20 			= "12.5 14.4 15.7 16.6 19.7 20.7"
gains_00_10 			= "0.0 0.9 1.4 2.7 3.7 7.7 8.7 12.5"

gains_all_40 			= "40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_all_30 			= "29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_all_20 			= "20.7 22.9 25.4 28.0 29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_all_10			= "12.5 14.4 15.7 16.6 19.7 20.7 22.9 25.4 28.0 29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6"
gains_all_00			= "0.0 0.9 1.4 2.7 3.7 7.7 8.7 12.5 14.4 15.7 16.6 19.7 20.7 22.9 25.4 28.0 29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6"

# REQUIRED SETTING
antenna_lat				= 33.444
antenna_lon				= -112.069
pass_duration			= 10
pass_number				= 5
gain_choice				= gains_all_20

# PIAWARE SD SETTINGS (comment out and uncomment other settings to switch)
host					= 'localhost'
port 					= 30003
config_file				= '/boot/piaware-config.txt'
config_setting			= 'rtlsdr-gain'
config_setting_after	= ''
service_restart_cmd		= 'sudo systemctl restart dump1090-fa'

# DUMP1090-FA on RASPBIAN
# host					= 'localhost'
# port 					= 30003
# config_file			= '/etc/default/dump1090-fa'
# config_setting		= 'RECEIVER_OPTIONS="--device-index 0 --ppm 0 --gain'
# config_setting_after	= '--net-bo-port 30005 --net-sbs-port 30003'
# service_restart_cmd	= 'sudo systemctl restart dump1090-fa'

# DUMP1090-MUTABILITY on RASPBIAN
# host					= 'localhost'
# port 					= 30003
# config_file			= '/etc/default/dump1090-mutability'
# config_setting		= 'GAIN='
# config_setting_after	= ''
# service_restart_cmd	= 'sudo systemctl restart dump1090-mutability'

# OPTIONAL SETTINGS
color_top_percent		= 5
distance_unit			= 'mile'	# changing distant_unit doesn't change category and column ranges currently therefore leave as miles

# CODE BELOW (DON'T CHANGE)

print(white + "REQUIRED SETTINGS:" + nocolor)
print("    antenna_lat          ", yellow + str(antenna_lat) + nocolor)
print("    antenna_lon          ", yellow + str(antenna_lon) + nocolor)
print("    pass_duration        ", yellow + str(pass_duration) + nocolor)
print("    pass_number          ", yellow + str(pass_number) + nocolor)
print("    gain_choice          ", yellow + str(gain_choice) + nocolor)
print(white + "REQUIRED DUMP1090 SETTINGS:" + nocolor)
print("    host                 ", yellow + str(host) + nocolor)
print("    port                 ", yellow + str(port) + nocolor)
print("    config_file          ", yellow + str(config_file) + nocolor)
print("    config_setting       ", yellow + str(config_setting) + nocolor)
print("    config_setting_after ", yellow + str(config_setting_after) + nocolor)
print("    service_restart_cmd  ", yellow + str(service_restart_cmd) + nocolor)
print(white + "OPTIONAL SETTINGS:" + nocolor)
print("    distance_unit        ", yellow + str(distance_unit) + nocolor)
print("    color_top_percent    ", yellow + str(color_top_percent) + nocolor)
print(line_break) #-----------------------------------------------------------------------------------------------------

# GREATCIRCLE ----------------------------------------------------------------------------------------------------------
def greatcircle(lat1, lon1, lat2, lon2, unit):
	R = 6370
	lat1 = radians(lat1)
	lon1 = radians(lon1)
	lat2 = radians(lat2)
	lon2 = radians(lon2)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1-a))

	distance = R * c
	if unit == 'mile':
		distance = distance * 0.6214
	distance = round(distance,1)

	return distance

# MAIN -----------------------------------------------------------------------------------------------------------------
gains 				= gain_choice.split()
results 			= {}
distances 			= {}
config_save_gain	= ''
script_time_start 	= time.time()
time_start 			= 0.00
time_end 			= 0.00

gains.reverse()

# PASS LOOP
for p in range(pass_number):

	# GAIN LOOP
	for g in gains:

		# SETUP STORAGE
		if g not in results:
			results[g]		= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		if g not in distances:
			distances[g]	= []

		# SET GAIN config_file (config_setting g config_setting_after)
		with open(config_file) as file:
		    file_list = list(file)

		with open(config_file, 'w') as output:
			for line in file_list:
				if line.startswith(config_setting):
					if config_save_gain == '':
						config_save_gain = line
						print("CONFIG_SAVE_GAIN    ", config_save_gain.replace("\n", ""))
					output.write(config_setting+space+g+space+config_setting_after+newline)
				else:
					output.write(line)
		# END SET GAIN config_file (config_setting g config_setting_after)

		print("PASS                     ", p+1, "of", pass_number)
		print("GAIN                     ", gains.index(g)+1, "of", len(gains))
		print("TESTING GAIN             ", g, "for", pass_duration, "SECONDS")
		print(line_dotted) #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
		print("LAST DATA ROUND SECS.    ", time_end)
		print("SCRIPT TOTAL SECONDS.    ", round(time.time() - script_time_start,2))
		print(line_break) #---------------------------------------------------------------------------------------------

		# RESTART service_restart_cmd & sleep 2 seconds
		os.system(service_restart_cmd)
		time.sleep(2)

		# OPEN SOCKET
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host,port))

		time_start	= time.time()
		data		= ''

		# COLLECT DATA LOOP
		while 1:
			data += s.recv(32).decode('utf-8')
			if time.time() - time_start > pass_duration:
				time_end = round(time.time() - time_start,2)
				break
		# END COLLECT DATA LOOP

		# CLOSE SOCKET
		s.close()

		# RESET MESSAGE VARIABLES
		total_messages		= 0
		type_1_id			= 0
		type_2_surface		= 0
		type_2_surface_pos	= 0
		type_3_airborn		= 0
		type_3_airborn_pos	= 0
		type_4_velocity		= 0
		type_5				= 0
		type_6				= 0
		type_7				= 0
		type_8				= 0
		aircraft_distances	= []

		# DATA LOOP
		for msg in data.split('\n'):
			# print(l)
			fields = msg.split(',')
			total_messages += 1
			if len(fields) > 1:
				if fields[1] == '1':
					type_1_id += 1
				if fields[1] == '2':
					type_2_surface += 1
					if len(fields) > 15:
						if fields[14] != '' and fields[15] != '':
							distance = greatcircle(antenna_lat,antenna_lon,float(fields[14]),float(fields[15]),distance_unit)
							aircraft_distances.append(distance)
							type_2_surface_pos += 1
				if fields[1] == '3':
					type_3_airborn += 1
					if len(fields) > 15:
						if fields[14] != '' and fields[15] != '':
							distance = greatcircle(antenna_lat,antenna_lon,float(fields[14]),float(fields[15]),distance_unit)
							aircraft_distances.append(distance)
							type_3_airborn_pos += 1
				if fields[1] == '4':
					type_4_velocity += 1
				if fields[1] == '5':
					type_5 += 1
				if fields[1] == '6':
					type_6 += 1
				if fields[1] == '7':
					type_7 += 1
				if fields[1] == '8':
					type_8 += 1
		# END DATA LOOP

		# RESET DISTANCE ANALYSIS VARIABLES
		distance_min		= 999
		distance_max		= -1
		distance_000_010 	= 0
		distance_000_050	= 0
		distance_050_100	= 0
		distance_100_150	= 0
		distance_150_200	= 0
		distance_200_250	= 0
		distance_250_300	= 0
		distance_300____	= 0

		distances[g] = distances[g] + aircraft_distances

		# CHECK ALL PASS DISTANCES for MAX/MIN
		for d in distances[g]:
			if d > distance_max:
				distance_max = d
			if d < distance_min and d > 0:
				distance_min = d

		# CHECK THIS PASS DISTANCES for RANGES
		for d in aircraft_distances: 
			if d >= 0 and d < 10:
				distance_000_010 +=1
			if d >= 0 and d < 50:
				distance_000_050 +=1
			if d >= 50 and d < 100:
				distance_050_100 +=1
			if d >= 100 and d < 150:
				distance_100_150 +=1
			if d >= 150 and d < 200:
				distance_150_200 +=1
			if d >= 200 and d < 250:
				distance_200_250 +=1
			if d >= 250 and d < 300:
				distance_250_300 +=1
			if d >= 300:
				distance_300____ +=1

		# SAVE PASS TO RESULTS
		results[g][0]		+= total_messages
		results[g][1]		+= type_1_id
		results[g][2]		+= type_2_surface
		results[g][3]		+= type_3_airborn
		results[g][4]		+= type_4_velocity
		results[g][5]		+= type_5
		results[g][6]		+= type_6
		results[g][7]		+= type_7
		results[g][8]		+= type_8
		if distance_min < results[g][9] or results[g][9] == 0:
			results[g][9]	= distance_min
		if distance_max > results[g][10]:
			results[g][10]	= distance_max
		results[g][11]		+= distance_000_010
		results[g][12]		+= distance_000_050
		results[g][13]		+= distance_050_100
		results[g][14]		+= distance_100_150
		results[g][15]		+= distance_150_200
		results[g][16]		+= distance_200_250
		results[g][17]		+= distance_250_300
		results[g][18]		+= distance_300____
		results[g][19]		+= type_2_surface_pos
		results[g][20]		+= type_3_airborn_pos
		results[g][21]		= g
		results[g][22]		= p+1

		# CLEAR & DISPLAY TABLE
		table = BeautifulTable(maxwidth=240)
		table_header = ['GAIN','PASS\nTOTAL','MSGS\nTOTAL\n1-8','MSGS\nTYPE_1\nID','MSGS\nTYPE_2\nGND_POS','MSGS\nTYPE_2\nGND_POS\nLATLON','MSGS\nTYPE_3\nAIR_POS','MSGS\nTYPE_3\nAIR_POS\nLATLON','MSGS\nTYPE_4\nVEL','MSGS\nTYPE_5','MSGS\nTYPE_6','MSGS\nTYPE_7','MSGS\nTYPE_8','DIST\nMIN','DIST\nMAX','DIST\n0-10\nCLS','DIST\n0-50','DIST\n50-100','DIST\n100-150','DIS\n150-200','DIST\n200-250\nFAR_1','DIST\n250-300\nFAR_2','DIST\n300+\nFAR_3']
		table.columns.header = table_header
		for g in results:
			row = [results[g][21],results[g][22],results[g][0],results[g][1],results[g][2],results[g][19],results[g][3],results[g][20],results[g][4],results[g][5],results[g][6],results[g][7],results[g][8],results[g][9],results[g][10],results[g][11],results[g][12],results[g][13],results[g][14],results[g][15],results[g][16],results[g][17],results[g][18]]
			table.rows.append(row)
		print(clear)
		print(line_break) #-----------------------------------------------------------------------------------------------------
		print("SCRIPT: ", white + script_name + nocolor)
		print("VERSION:", white + script_version + space + script_release + nocolor)
		print("AUTHOR: ", white + script_author  + nocolor)
		print(table)

	# END GAIN LOOP
# END PASS LOOP

print(clear)
print(line_break) #-----------------------------------------------------------------------------------------------------
print("SCRIPT: ", white + script_name + nocolor)
print("VERSION:", white + script_version + space + script_release + nocolor)
print("AUTHOR: ", white + script_author  + nocolor)
print(line_break) #-----------------------------------------------------------------------------------------------------
print("RESTORE GAIN TO", config_save_gain.replace("\n", ""), "RESTART SERVICE", service_restart_cmd)

# RESET GAIN to ORIGINAL config_file config_save_gain
if config_save_gain != '':
	with open(config_file, 'w') as output:
		for line in file_list:
			if line.startswith(config_setting):
				output.write(config_save_gain)
			else:
				output.write(line)

# RESTART service_restart_cmd
os.system(service_restart_cmd)

# PRINTING FINAL COLOR TABLE
gain_best_all 					= []
gain_best_important_subset		= []
gain_best_msgs_total			= []
gain_best_msgs_types_all 		= []
gain_best_msgs_types_pos		= []
gain_best_msgs_types_pos_ll		= []
gain_best_distance_min 			= []
gain_best_distance_max 			= []
gain_best_distance_all 			= []
gain_best_distance_cls 			= []
gain_best_distance_nrm 			= []
gain_best_distance_far 			= []

table_header_msgs_total			= ['MSGS\nTOTAL\n1-8']

table_header_msgs_types_145678	= ['MSGS\nTYPE_1\nID','MSGS\nTYPE_4\nVEL','MSGS\nTYPE_5','MSGS\nTYPE_6','MSGS\nTYPE_7','MSGS\nTYPE_8']
table_header_msgs_types_pos		= ['MSGS\nTYPE_2\nGND_POS','MSGS\nTYPE_3\nAIR_POS']
table_header_msgs_types_pos_ll	= ['MSGS\nTYPE_2\nGND_POS\nLATLON','MSGS\nTYPE_3\nAIR_POS\nLATLON']
table_header_msgs_types_all		= table_header_msgs_types_145678 + table_header_msgs_types_pos + table_header_msgs_types_pos_ll

table_header_msgs_distance_min	= ['DIST\nMIN']
table_header_msgs_distance_max	= ['DIST\nMAX']

table_header_msgs_distance_cls	= ['DIST\n0-10\nCLS']
table_header_msgs_distance_nrm	= ['DIST\n0-50','DIST\n50-100','DIST\n100-150','DIS\n150-200']
table_header_msgs_distance_far	= ['DIST\n200-250\nFAR_1','DIST\n250-300\nFAR_2','DIST\n300+\nFAR_3']
table_header_msgs_distance_all	= table_header_msgs_distance_cls + table_header_msgs_distance_nrm + table_header_msgs_distance_far

table_header_important			= table_header_msgs_total + table_header_msgs_types_pos_ll + table_header_msgs_distance_min + table_header_msgs_distance_max + table_header_msgs_distance_nrm
table_header_all 				= table_header_msgs_total + table_header_msgs_types_all + table_header_msgs_distance_max + table_header_msgs_distance_min + table_header_msgs_distance_all
table_header_min 				= table_header_msgs_distance_min

# RANKING & COLOR
for column_name in table_header_all:

	# RESET variables
	column_value 		= 0
	column_value_str	= ""
	column_index 		= 0
	column_total		= 0

	# GET list
	column_list = list(table.columns[column_name])

	# GET min/max
	if column_name in table_header_min:
		column_value = min(column_list)
		column_index = column_list.index(min(column_list))
	else:
		column_value = max(column_list)
		column_index = column_list.index(max(column_list))

	# SET table color & ranking (CHECK not 0)
	if column_value > 0:

		# SET table color top percent (cyan)
		for item in column_list:
			if item > 0:
				if column_name in table_header_min:
					item_percentage_dif = (1 - (column_value / item)) * 100
				else: 
					item_percentage_dif = (1 - (item / column_value)) * 100
				if item_percentage_dif < color_top_percent:
					column_percentage_index = column_list.index(item)
					column_percentage_value_str = white + str(item) + nocolor
					table.rows[column_percentage_index][column_name] = column_percentage_value_str

		# SET table color best (green)
		column_value_str = green + str(column_value) + nocolor
		table.rows[column_index][column_name] = column_value_str

		# SET ranking
		gain_best_all.append(table.columns['GAIN'][column_index])
		if column_name in table_header_important:
			gain_best_important_subset.append(table.columns['GAIN'][column_index])

		if column_name in table_header_msgs_total:
			gain_best_msgs_total.append(table.columns['GAIN'][column_index])
		if column_name in table_header_msgs_types_all:
			gain_best_msgs_types_all.append(table.columns['GAIN'][column_index])
		if column_name in table_header_msgs_types_pos:
			gain_best_msgs_types_pos.append(table.columns['GAIN'][column_index])
		if column_name in table_header_msgs_types_pos_ll:
			gain_best_msgs_types_pos_ll.append(table.columns['GAIN'][column_index])

		if column_name in table_header_msgs_distance_max:
			gain_best_distance_max.append(table.columns['GAIN'][column_index])
		if column_name in table_header_msgs_distance_min:
			gain_best_distance_min.append(table.columns['GAIN'][column_index])

		if column_name in table_header_msgs_distance_cls:
			gain_best_distance_cls.append(table.columns['GAIN'][column_index])
		if column_name in table_header_msgs_distance_nrm:
			gain_best_distance_nrm.append(table.columns['GAIN'][column_index])
		if column_name in table_header_msgs_distance_far:
			gain_best_distance_far.append(table.columns['GAIN'][column_index])
		if column_name in table_header_msgs_distance_all:
			gain_best_distance_all.append(table.columns['GAIN'][column_index])

# DISPLAY MOST COMMMON for EACH gain_best

print(line_break) #-----------------------------------------------------------------------------------------------------
print("GAIN SETTING which is" + green + " BEST " + nocolor + "for each CATEGORY (none means no data for that category)")
print(line_break) #-----------------------------------------------------------------------------------------------------
print("best gain overall (all categories)               ",green + str(max(set(gain_best_all), 				key=gain_best_all.count)) + nocolor 				if len(set(gain_best_all)) 				 > 0 else "none")
print("best gain overall (important subsets)            ",green + str(max(set(gain_best_important_subset), 	key=gain_best_important_subset.count)) + nocolor 	if len(set(gain_best_important_subset))  > 0 else "none")
print(line_dotted) #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
print("best gain messages total received                ",green + str(max(set(gain_best_msgs_total), 		key=gain_best_msgs_total.count)) + nocolor 			if len(set(gain_best_msgs_total)) 		 > 0 else "none")
print("best gain messages types 1-8 (all)               ",green + str(max(set(gain_best_msgs_types_all), 	key=gain_best_msgs_types_all.count)) + nocolor 		if len(set(gain_best_msgs_types_all)) 	 > 0 else "none")
print("best gain messages types 2,3 (pos)               ",green + str(max(set(gain_best_msgs_types_pos), 	key=gain_best_msgs_types_pos.count)) + nocolor 		if len(set(gain_best_msgs_types_pos)) 	 > 0 else "none")
print("best gain messages types 2,3 (pos w/ latlon only)",green + str(max(set(gain_best_msgs_types_pos_ll), key=gain_best_msgs_types_pos_ll.count)) + nocolor 	if len(set(gain_best_msgs_types_pos_ll)) > 0 else "none")
print(line_dotted) #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
print("best gain distance minimum                       ",green + str(max(set(gain_best_distance_min), 		key=gain_best_distance_min.count)) + nocolor 		if len(set(gain_best_distance_min)) 	 > 0 else "none")
print("best gain distance maximum                       ",green + str(max(set(gain_best_distance_max), 		key=gain_best_distance_max.count)) + nocolor 		if len(set(gain_best_distance_max)) 	 > 0 else "none")
print(line_dotted) #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
print("best gain distance 0-300+   miles (all)          ",green + str(max(set(gain_best_distance_all), 		key=gain_best_distance_all.count)) + nocolor 		if len(set(gain_best_distance_all)) 	 > 0 else "none")
print("best gain distance 0-10     miles (close)        ",green + str(max(set(gain_best_distance_cls), 		key=gain_best_distance_cls.count)) + nocolor 		if len(set(gain_best_distance_cls)) 	 > 0 else "none")
print("best gain distance 0-200    miles (normal)       ",green + str(max(set(gain_best_distance_nrm), 		key=gain_best_distance_nrm.count)) + nocolor 		if len(set(gain_best_distance_nrm)) 	 > 0 else "none")
print("best gain distance 200-300+ miles (far)          ",green + str(max(set(gain_best_distance_far), 		key=gain_best_distance_far.count)) + nocolor 		if len(set(gain_best_distance_far)) 	 > 0 else "none")
print(line_break) #-----------------------------------------------------------------------------------------------------
print(nocolor + "FINAL TABLE with" + green + " GREEN BEST " + nocolor + "and" + white + " WHITE within " + red +  str(color_top_percent) + "%" + white + " of BEST VALUE" + nocolor)
print(table)
print(line_break) #-----------------------------------------------------------------------------------------------------
print("FINISHED...", "SCRIPT TOTAL SECONDS", round(time.time() - script_time_start,2))
print(line_break) #-----------------------------------------------------------------------------------------------------
