# BVG/Weather E-paper display
Generate high-contrast 1-bit .bin images (useful for e-paper displays)
Can be used with [PicoEpaperCast](https://github.com/karanmhatre1/Pico-Epaper-Cast) or any e-paper client that downloads and displays binary frames.

![https://res.cloudinary.com/dgksx9vlc/image/upload/w_600/q_auto/V3_t7peqv.png](https://res.cloudinary.com/dgksx9vlc/image/upload/w_600/q_auto/V3_t7peqv.png)

This project generates a 600×448 black-and-white image containing:
- Live BVG public transport departures
- Weather forecast
- Fully rendered layout using Pillow
- Output saved as a compact binary file (output.bin) ready for e-ink displays

## Features
- Fetches live BVG transport data (Using the BVG API - https://v6.bvg.transport.rest/)
- Fetches live weather (from [Weather API](https://www.weatherapi.com/))
- Uses Pillow (PIL) to render a clean, readable board-style layout
- Converts the image to 1-bit e-paper format for Waveshare 5.83" display
- Outputs a lightweight output.bin
- Build to run continuously at the defined refresh rate

## Configuration
- Add your API key from [Weather API](https://www.weatherapi.com/) in the ```main.py``` file ```WEATHER_API_KEY = "ADD YOUR API KEY HERE"```
- You can make edits to the Figma file and replace the ```ui.png``` file in the main folder - [Figma File](https://www.figma.com/design/cjOshCGQh8pGtSLoRhdFYi/Bvg-Weather-E-paper-Display?node-id=0-1&t=FPMxVGQMMeU3O5G2-1). If you change the position of where the timings and temperature appear, then you may also need to change the coordinates of the text in ```main.py```

## Compatible With
This repo works perfectly with:
[Pico Epaper Cast](https://github.com/karanmhatre1/Pico-Epaper-Cast)


