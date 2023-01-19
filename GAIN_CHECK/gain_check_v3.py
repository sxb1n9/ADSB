#!/usr/bin/python3
import time, socket, subprocess, fileinput, os
from math import sin, cos, sqrt, atan2, radians
from beautifultable import BeautifulTable

# COLORS
black				= "\033[0;30m"
red 				= "\033[0;31m"
green 				= "\033[0;32m"
yellow 				= "\033[0;33m"
blue 				= "\033[0;34m"
pink 				= "\033[0:35m"
teal 				= "\033[0:36m"
white 				= "\033[0;37m"
nocolor 			= "\033[0m"

# HEADER
print(chr(27) + "[2J")
print("--------------------------------------------------------------------------------")
print(blue + "SCRIPT  gain_check_v3.py" + nocolor)
print(blue + "VERSION 3.2" + nocolor)
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
# 	keep aircraft distance between all passes (started distances array but not finished)
# 	add seconds while receiving gain info
# 3.2
# 	not detecting minimums correctly
# 	not counting distance msgs correctly
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
# 	RANKING
#		best        teal    +2
#		top 5%      blue    +1
#		middle		norm	0
# 		bottom 5%   pink    -1
# 		worst       red     -2
# 	settings for ranking top and bottom percentages
# 	display gain ranking numbers 
#	display colored table and ranking at end of each pass and don't clear right away 
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

# CODE BELOW (DON'T CHANGE)

print("STARTING BELOW ARE THE CONFIG CHANGEABLE SETTINGS")
print("--------------------------------------------------------------------------------")
print("antenna_lat          ", red + str(antenna_lat) + nocolor)
print("antenna_lon          ", red + str(antenna_lon) + nocolor)
print("pass_duration        ", red + str(pass_duration) + nocolor)
print("pass_number          ", red + str(pass_number) + nocolor)
print("gain_choice          ", red + str(gain_choice) + nocolor)
print("host                 ", red + str(host) + nocolor)
print("port                 ", red + str(port) + nocolor)
print("config_file          ", red + str(config_file) + nocolor)
print("config_name          ", red + str(config_name) + nocolor)
print("config_setting       ", red + str(config_setting) + nocolor)
print("config_setting_2     ", red + str(config_setting_2) + nocolor)
print("service_restart_cmd  ", red + str(service_restart_cmd) + nocolor)
print("--------------------------------------------------------------------------------")

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
			distances[g] 	= []

		# SET GAIN config_file config_name
		with open(config_file) as file:
		    file_list = list(file)

		with open(config_file, 'w') as output:
			for line in file_list:
				if line.startswith(config_name):
					if config_save_gain == '':
						config_save_gain = line
						print("CONFIG_SAVE_GAIN     ", config_save_gain.replace("\n", ""))
					output.write(config_name+' '+g+'\n')
				else:
					output.write(line)
		# END SET GAIN config_file config_name

		print("PASS                 ", p+1, "of", pass_number)
		print("GAIN                 ", gains.index(g)+1, "of", len(gains))
		print("TESTING GAIN         ", g, "for", pass_duration, "SECONDS")
		print("--------------------------------------------------------------------------------")
		print("SECS LAST DATA ROUND ", time_end)
		print("SECS SCRIPT TOTAL    ", round(time.time() - script_time_start,2))
		print("--------------------------------------------------------------------------------")

		# RESTART service_restart_cmd
		os.system(service_restart_cmd)

		time.sleep(2)

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host,port))

		time_start 	= time.time()
		data 		= ''

		# COLLECT DATA LOOP
		while 1:
			data += s.recv(32).decode('utf-8')
			if time.time() - time_start > pass_duration:
				break
		# END COLLECT DATA LOOP

		time_end    = round(time.time() - time_start,2)

		s.close()

		total_messages		= 0
		type_1_id			= 0
		type_2_surface 		= 0
		type_2_surface_pos	= 0
		type_3_airborn 		= 0
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
					if len(fields) > 15:
						type_2_surface += 1
						if fields[14] != '' and fields[15] != '':
							distance = greatcircle(antenna_lat,antenna_lon,float(fields[14]),float(fields[15]),distance_unit)
							aircraft_distances.append(distance)
							type_2_surface_pos += 1
				if fields[1] == '3':
					if len(fields) > 15:
						type_3_airborn += 1
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

		# DISTANCE ANALYSIS
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

		for d in distances[g]:
			if d > distance_max:
				distance_max = d
			if d < distance_min and d > 0:
				distance_min = d
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

		# DISPLAY PASS (V2 and PYTHON 2)
		# print("GAIN                    ", g)
		# print("msgs_total              ", total_messages)
		# print("msgs_type_1_id          ", type_1_id)
		# print("msgs_type_2_surface_pos ", type_2_surface_pos)
		# print("msgs_type_3_airborn_pos ", type_3_airborn_pos)
		# print("msgs_type_4_velocity    ", type_4_velocity)
		# print("distance_max            ", distance_max)
		# print("distance_min            ", distance_min)
		# print("   000 - 010 close      ", distance_000_010)
		# print("   000 - 050            ", distance_000_050)
		# print("   050 - 100            ", distance_050_100)
		# print("   100 - 150            ", distance_100_150)
		# print("   150 - 200            ", distance_150_200)
		# print("   200 - 250 far        ", distance_200_250)
		# print("   250 - 300 far x2     ", distance_250_300)
		# print("       > 300 far x3     ", distance_300____)

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
		results[g][19]		+= type_3_airborn_pos
		results[g][20]		+= type_2_surface_pos
		results[g][21]		= g
		results[g][22]		= p+1

		# CLEAR & DISPLAY TABLE
		table = BeautifulTable(maxwidth=200)
		table.columns.header = ['GAIN','PASS\nTOTAL','MSGS\nTOTAL\n1-8','MSGS\nTYPE_1\nID','MSGS\nTYPE_2\nGND_POS','MSGS\nTYPE_3\nAIR_POS','MSGS\nTYPE_4\nVEL','MSGS\nTYPE_5','MSGS\nTYPE_6','MSGS\nTYPE_7','MSGS\nTYPE_8','DIST\nMIN','DIST\nMAX','DIST\n0-10\nCLS','DIST\n0-50','DIST\n50-100','DIST\n100-150','DIS\n150-200','DIST\n200-250\nFAR_1','DIST\n250-300\nFAR_2','DIST\n300+\nFAR_3']
		for g in results:
			row = [results[g][21],results[g][22],results[g][0],results[g][1],results[g][2],results[g][3],results[g][4],results[g][5],results[g][6],results[g][7],results[g][8],results[g][9],results[g][10],results[g][11],results[g][12],results[g][13],results[g][14],results[g][15],results[g][16],results[g][17],results[g][18]]
			table.rows.append(row)
		print(chr(27) + "[2J")
		print(table)

	# END GAIN LOOP
# END PASS LOOP

print(chr(27) + "[2J")

print("--------------------------------------------------------------------------------")
print("RESTORE GAIN BACK TO ORIGINAL CONFIG_SAVE_GAIN  ", config_save_gain.replace("\n", ""))
print("RESTART SERVICE  ", service_restart_cmd)

# RESET GAIN to ORIGINAL config_file config_save_gain
if config_save_gain != '':
	with open(config_file, 'w') as output:
		for line in file_list:
			if line.startswith(config_name):
				output.write(config_save_gain)
			else:
				output.write(line)

# RESTART service_restart_cmd
os.system(service_restart_cmd)

print("FINDING BEST VALUES & HIGHLIGHTING BEST CELLS")
print("--------------------------------------------------------------------------------")

# PRINTING FINAL COLOR TABLE
gain_best_all 				= []
gain_best_important_subset	= []
gain_best_msgs_total		= []
gain_best_msgs_types_all 	= []
gain_best_msgs_types_pos	= []
gain_best_distance_min 		= []
gain_best_distance_max 		= []
gain_best_distance_all 		= []
gain_best_distance_cls 		= []
gain_best_distance_nrm 		= []
gain_best_distance_far 		= []

# MAX for MSGS TOTAL
for m in ['MSGS\nTOTAL\n1-8']:
	column_name 		= m
	column_list 		= list(table.columns[column_name])
	column_max 			= max(column_list)
	column_max_index 	= column_list.index(max(column_list))
	column_update 		= green + str(column_max) + nocolor
	if column_max > 0:
		table.rows[column_max_index][column_name] = column_update
		# update gain_best's
		gain_best_all.append(table.columns['GAIN'][column_max_index])
		gain_best_important_subset.append(table.columns['GAIN'][column_max_index])
		gain_best_msgs_total.append(table.columns['GAIN'][column_max_index])

# MAX for MSGS TYPES 1,4,5,6,7,8
for m in ['MSGS\nTYPE_1\nID','MSGS\nTYPE_4\nVEL','MSGS\nTYPE_5','MSGS\nTYPE_6','MSGS\nTYPE_7','MSGS\nTYPE_8']:
	column_name 		= m
	column_list 		= list(table.columns[column_name])
	column_max 			= max(column_list)
	column_max_index 	= column_list.index(max(column_list))
	column_update 		= green + str(column_max) + nocolor
	if column_max > 0:
		table.rows[column_max_index][column_name] = column_update
		# update gain_best's
		gain_best_all.append(table.columns['GAIN'][column_max_index])
		gain_best_msgs_types_all.append(table.columns['GAIN'][column_max_index])

# MAX for MSGS POS 2,3
for m in ['MSGS\nTYPE_2\nGND_POS','MSGS\nTYPE_3\nAIR_POS']:
	column_name 		= m
	column_list 		= list(table.columns[column_name])
	column_max 			= max(column_list)
	column_max_index 	= column_list.index(max(column_list))
	column_update 		= green + str(column_max) + nocolor
	if column_max > 0:
		table.rows[column_max_index][column_name] = column_update
		# update gain_best's
		gain_best_all.append(table.columns['GAIN'][column_max_index])
		gain_best_important_subset.append(table.columns['GAIN'][column_max_index])
		gain_best_msgs_types_all.append(table.columns['GAIN'][column_max_index])
		gain_best_msgs_types_pos.append(table.columns['GAIN'][column_max_index])

# MIN for DISTANCE MIN
for m in ['DIST\nMIN']:
	column_name 		= m
	column_list 		= list(table.columns[column_name])
	column_min 			= min(column_list)
	column_min_index 	= column_list.index(min(column_list))
	column_update 		= green + str(column_min) + nocolor
	if column_max > 0:
		table.rows[column_min_index][column_name] = column_update
		# update gain_best's
		gain_best_all.append(table.columns['GAIN'][column_min_index])
		gain_best_important_subset.append(table.columns['GAIN'][column_min_index])
		gain_best_distance_min.append(table.columns['GAIN'][column_min_index])

# MAX for DISTANCE MAX
for m in ['DIST\nMAX']:
	column_name 		= m
	column_list 		= list(table.columns[column_name])
	column_max 			= max(column_list)
	column_max_index 	= column_list.index(max(column_list))
	column_update 		= green + str(column_max) + nocolor
	if column_max > 0:
		table.rows[column_max_index][column_name] = column_update
		# update gain_best's
		gain_best_all.append(table.columns['GAIN'][column_max_index])
		gain_best_important_subset.append(table.columns['GAIN'][column_max_index])
		gain_best_distance_max.append(table.columns['GAIN'][column_max_index])

# MAX for DISTANCE CLS
for m in ['DIST\n0-10\nCLS']:
	column_name 		= m
	column_list 		= list(table.columns[column_name])
	column_max 			= max(column_list)
	column_max_index 	= column_list.index(max(column_list))
	column_update 		= green + str(column_max) + nocolor
	if column_max > 0:
		table.rows[column_max_index][column_name] = column_update
		# update gain_best's
		gain_best_all.append(table.columns['GAIN'][column_max_index])
		gain_best_distance_all.append(table.columns['GAIN'][column_max_index])
		gain_best_distance_cls.append(table.columns['GAIN'][column_max_index])

# MAX for DISTANCE 0-200
for m in ['DIST\n0-50','DIST\n50-100','DIST\n100-150','DIS\n150-200']:
	column_name 		= m
	column_list 		= list(table.columns[column_name])
	column_max 			= max(column_list)
	column_max_index 	= column_list.index(max(column_list))
	column_update 		= green + str(column_max) + nocolor
	if column_max > 0:
		table.rows[column_max_index][column_name] = column_update
		# update gain_best's
		gain_best_all.append(table.columns['GAIN'][column_max_index])
		gain_best_important_subset.append(table.columns['GAIN'][column_max_index])
		gain_best_distance_all.append(table.columns['GAIN'][column_max_index])
		gain_best_distance_nrm.append(table.columns['GAIN'][column_max_index])

# MAX for DISTANCE 200-300+ FAR
for m in ['DIST\n200-250\nFAR_1','DIST\n250-300\nFAR_2','DIST\n300+\nFAR_3']:
	column_name 		= m
	column_list 		= list(table.columns[column_name])
	column_max 			= max(column_list)
	column_max_index 	= column_list.index(max(column_list))
	column_update 		= green + str(column_max) + nocolor
	if column_max > 0:
		table.rows[column_max_index][column_name] = column_update
		# update gain_best's
		gain_best_all.append(table.columns['GAIN'][column_max_index])
		gain_best_important_subset.append(table.columns['GAIN'][column_max_index])
		gain_best_distance_all.append(table.columns['GAIN'][column_max_index])
		gain_best_distance_far.append(table.columns['GAIN'][column_max_index])

# DISPLAY MOST COMMMON for EACH gain_best

print("BELOW SHOWS WHICH GAIN WINS EACH CATEGORY")
print("--------------------------------------------------------------------------------")
print("gain_best_all (overall)     ",green + str(max(set(gain_best_all), key=gain_best_all.count)) + nocolor)
print("gain_best_important_subset  ",green + str(max(set(gain_best_important_subset), key=gain_best_important_subset.count)) + nocolor)
print("gain_best_msgs_total        ",green + str(max(set(gain_best_msgs_total), key=gain_best_msgs_total.count)) + nocolor)
print("gain_best_msgs_types_all    ",green + str(max(set(gain_best_msgs_types_all), key=gain_best_msgs_types_all.count)) + nocolor)
print("gain_best_msgs_types_pos    ",green + str(max(set(gain_best_msgs_types_pos), key=gain_best_msgs_types_pos.count)) + nocolor)
print("gain_best_distance_min      ",green + str(max(set(gain_best_distance_min), key=gain_best_distance_min.count)) + nocolor)
print("gain_best_distance_max      ",green + str(max(set(gain_best_distance_max), key=gain_best_distance_max.count)) + nocolor)
print("gain_best_distance_all      ",green + str(max(set(gain_best_distance_all), key=gain_best_distance_all.count)) + nocolor)
print("gain_best_distance_cls      ",green + str(max(set(gain_best_distance_cls), key=gain_best_distance_cls.count)) + nocolor)
print("gain_best_distance_nrm      ",green + str(max(set(gain_best_distance_nrm), key=gain_best_distance_nrm.count)) + nocolor)
print("gain_best_distance_far      ",green + str(max(set(gain_best_distance_far), key=gain_best_distance_far.count)) + nocolor)
print("--------------------------------------------------------------------------------")
print("BELOW SHOWS the FINAL TABLE with HIGHLIGHTED BESTS")
print("--------------------------------------------------------------------------------")
print(table)
print("--------------------------------------------------------------------------------")
print("FINISHED")
print("SECS SCRIPT TOTAL    ", round(time.time() - script_time_start,2))
print("--------------------------------------------------------------------------------")
