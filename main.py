import requests
from datetime import datetime, timezone
from collections import defaultdict
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import time
from helper import image_to_bin, shorten_stop_name

# Get a key from https://www.weatherapi.com/
WEATHER_API_KEY = "WEATHER API KEY HERE"

BVG_DATA = defaultdict(lambda: defaultdict(list))
PLATFORM_DESTINATION = defaultdict(lambda: defaultdict(list))

WEATHER_DATA = {}

stops_and_lines = {
	"900100016": {
		"142": "240",
		"U2": "360"
	}
}

def set_bvg_data():

	BVG_DATA.clear()

	now_time = datetime.now(timezone.utc)

	for stop_id, stop_data in stops_and_lines.items():
		stops_data_url = "https://v6.bvg.transport.rest/stops/"+ stop_id +"/departures?duration=60"
		response = requests.get(stops_data_url)
		data = response.json()

		# print(data)

		for x in data['departures']:
			line_name = x['line']['name']
			destination = x['direction']
			platform = x['platform']

			if any(line_name in stop for stop in stops_and_lines.values()) and x['when'] is not None:
				v_time = datetime.fromisoformat(x['when'])
				diff = v_time - now_time

				offset = stop_data.get("line_name", 120)
				time_diff = round((diff.total_seconds() - offset) / 60)
				
				if time_diff > 0 and len(BVG_DATA[line_name][platform]) < 2:
					PLATFORM_DESTINATION[line_name][platform] = destination
					BVG_DATA[line_name][platform].append(time_diff)

def set_weather_data():
	weather_url = "https://api.weatherapi.com/v1/current.json?q=Berlin&key="+WEATHER_API_KEY
	response = requests.get(weather_url)
	data = response.json()

	temp = data['current']['feelslike_c']
	rain = data['current']['precip_mm']
	cloud = data['current']['cloud']

	WEATHER_DATA['temp'] = round(temp)
	WEATHER_DATA['rain'] = rain
	WEATHER_DATA['sun'] = (cloud < 20)
	

def generate_image():

	set_bvg_data()
	set_weather_data()
	
	image = Image.new("1", (648, 480), "white")
	draw = ImageDraw.Draw(image)
	font = ImageFont.truetype("berlin.ttf", size=42)
	font_l = ImageFont.truetype("berlin.ttf", size=64)
	font_xl = ImageFont.truetype("berlin.ttf", size=78)
	
	# UI

	ui = Image.open('ui.png')
	image.paste(ui, (0, 0), ui)

	flag = [0,0,0,0]

	# print(BVG_DATA)

	for index1, (line, platform) in enumerate(BVG_DATA.items()):

		if index1 == 0:
			draw.text((36, 63), line, font=font_l, fill=0)
		else:
			draw.text((36, 243), line, font=font_l, fill=0)

		for index, (platform_name, timings) in enumerate(platform.items()):
			if index1 == 0:
				if index == 0:
					draw.text((139, 41), "'" + shorten_stop_name(PLATFORM_DESTINATION[line][platform_name]), font=font, fill=0)
					draw.text((438, 26), "'" + str(timings[0]), font=font_l, fill=0)
					draw.text((540, 26), "'" + str(timings[1]), font=font_l, fill=0)
				else:
					draw.text((139, 116), "'" + shorten_stop_name(PLATFORM_DESTINATION[line][platform_name]), font=font, fill=0)
					draw.text((438, 105), "'"+ str(timings[0]), font=font_l, fill=0)
					draw.text((540, 105), "'" + str(timings[1]), font=font_l, fill=0)
			else:
				if index == 0:
					draw.text((139, 220), "'" + shorten_stop_name(PLATFORM_DESTINATION[line][platform_name]), font=font, fill=0)
					draw.text((438, 212), "'" + str(timings[0]), font=font_l, fill=0)
					draw.text((540, 212), "'" + str(timings[1]), font=font_l, fill=0)
				else:
					draw.text((139, 290), "'" + shorten_stop_name(PLATFORM_DESTINATION[line][platform_name]), font=font, fill=0)
					draw.text((438, 283), "'"+ str(timings[0]), font=font_l, fill=0)
					draw.text((540, 283), "'" + str(timings[1]), font=font_l, fill=0)
	
	## Weather

	u_on = Image.open('u-on.png')
	u_off = Image.open('u-off.png')

	coat_on = Image.open('coat-on.png')
	coat_off = Image.open('coat-off.png')

	glove_on = Image.open('glove-on.png')
	glove_off = Image.open('glove-off.png')

	cap_on = Image.open('cap-on.png')
	cap_off = Image.open('cap-off.png')

	draw.text((36, 394), str(WEATHER_DATA["temp"]) + "°C", font=font_xl, fill=0)

	if WEATHER_DATA["rain"] > 0.5:
		image.paste(u_off, (296, 400), u_off)
	else:
		image.paste(u_on, (296, 400), u_on)

	if WEATHER_DATA["temp"] < 5:
		image.paste(glove_on, (558, 400), glove_on)
	else: 
		image.paste(glove_off, (558, 400), glove_off)

	if WEATHER_DATA["temp"] < 15:
		image.paste(coat_on, (380, 400), coat_on)
	else: 
		image.paste(glove_off, (558, 400), glove_off)

	image.paste(cap_off, (468, 400), cap_off)

	image.save("result.png")

	EPD_WIDTH  = 648
	EPD_HEIGHT = 480

	INPUT_IMAGE = "connect_wifi_2.png"
	OUTPUT_BIN  = "output.bin"

	image_to_bin(INPUT_IMAGE, OUTPUT_BIN, EPD_WIDTH, EPD_HEIGHT, invert=True)

# image_to_bin("connect_wifi_1.png", "output.bin", 648, 480, invert=True)

# generate_image()
while(True):
	try:
	  generate_image()
	except:
	  print("An exception occurred") 
	  
	time.sleep(60)