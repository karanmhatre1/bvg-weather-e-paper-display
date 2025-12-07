import requests
from datetime import datetime, timezone
from collections import defaultdict
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import time


WEATHER_API_KEY = "ADD YOUR API KEY HERE"

BVG_DATA = defaultdict(lambda: defaultdict(list))
WEATHER_DATA = {}

LINE_OFFSETS = {
    "M8": 240,
    "U2": 420,
}
DEFAULT_OFFSET = 420

def image_to_epd_bin(in_path, out_path, width, height, invert=False):
  img = cv2.imread(in_path, cv2.IMREAD_GRAYSCALE)
  if img is None:
      raise RuntimeError(f"Could not read image: {in_path}")

  img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
  _, bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)

  if invert:
      bw = 255 - bw
  buf = np.full((height * width // 8,), 0xFF, dtype=np.uint8)

  for y in range(height):
      for x in range(width):
          pixel = bw[y, x]  # 0 or 255
          if pixel == 0:    # black pixel
              index = (x // 8) + y * (width // 8)
              bit = 0x80 >> (x % 8)
              buf[index] &= (~bit & 0xFF)

  buf.tofile(out_path)

def set_bvg_data():

	BVG_DATA.clear()

	url = "https://v6.bvg.transport.rest/stops/900100016/departures?duration=60"

	now_time = datetime.now(timezone.utc);
	response = requests.get(url)
	data = response.json()

	for x in data['departures']:
		line_name = x['line']['name']
		direction = x['direction']
		
		v_time = datetime.fromisoformat(x['when'])
		diff = v_time - now_time

		offset = LINE_OFFSETS.get(line_name, DEFAULT_OFFSET)
		time_diff = round((diff.total_seconds() - offset) / 60)
		
		if time_diff > 0:
			BVG_DATA[line_name][direction].append(time_diff)

def set_weather_data():
	weather_url = "https://api.weatherapi.com/v1/current.json?q=Berlin&key="+WEATHER_API_KEY
	response = requests.get(weather_url)
	data = response.json()

	temp = data['current']['feelslike_c']
	rain = data['current']['precip_mm']

	WEATHER_DATA['temp'] = round(temp)
	WEATHER_DATA['rain'] = rain

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

	for type, directions in BVG_DATA.items():
		if type == "M8":
			for direction, timings in directions.items():
				if "Hauptbahnhof" in direction:
					if flag[0] == 0:
						if len(timings) >= 1:
							draw.text((438, 26), "'" + str(timings[0]), font=font_l, fill=0)
						if len(timings) >= 2:
							draw.text((540, 26), "'" + str(timings[1]), font=font_l, fill=0)
						flag[0] = 1
				else:
					if flag[1] == 0:
						if len(timings) >= 1:
							draw.text((438, 105), "'"+ str(timings[0]), font=font_l, fill=0)
						if len(timings) >= 2:
							draw.text((540, 105), "'" + str(timings[1]), font=font_l, fill=0)
						flag[1] = 1

		if type == "U2":
			for direction, timings in directions.items():
				if "Pankow" in direction:
					if flag[2] == 0:
						if len(timings) >= 1:
							draw.text((438, 212), "'" + str(timings[0]), font=font_l, fill=0)
						if len(timings) >= 2:
							draw.text((540, 212), "'" + str(timings[1]), font=font_l, fill=0)
						flag[2] = 1
				else:
					if flag[3] == 0:
						if len(timings) >= 1:
							draw.text((438, 283), "'"+ str(timings[0]), font=font_l, fill=0)
						if len(timings) >= 2:
							draw.text((540, 283), "'" + str(timings[1]), font=font_l, fill=0)
						flag[3] = 1
	
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

	INPUT_IMAGE = "result.png"
	OUTPUT_BIN  = "output.bin"

	image_to_epd_bin(INPUT_IMAGE, OUTPUT_BIN, EPD_WIDTH, EPD_HEIGHT, invert=True)

while(True):
	try:
	  generate_image()
	except:
	  print("An exception occurred") 
	  
	time.sleep(60)