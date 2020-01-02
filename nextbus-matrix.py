 # NextBus scrolling marquee display for Adafruit RGB LED matrix (64x32).
# Requires rgbmatrix.so library: github.com/adafruit/rpi-rgb-led-matrix

import atexit
import Image
import ImageDraw
import ImageFont
import math
import os
import time
from predict import predict
from rgbmatrix import Adafruit_RGBmatrix

# Configurable stuff ---------------------------------------------------------

# List of bus lines/stops to predict.  Use routefinder.py to look up
# lines/stops for your location, copy & paste results here.  The 4th
# string on each line can then be edited for brevity if desired.
stops = [
    ('sf-muni', 'N', '7318', 'Inbound'),
    ('sf-muni', '24', '4330', 'Castro'),
    ('sf-muni', '24', '4331', 'Divis'),
#   ('sf-muni', '22', '5018', 'Mission'),
]

maxPredictions = 3   # NextBus shows up to 5; limit to 3 for simpler display
minTime        = 0   # Drop predictions below this threshold (minutes)
shortTime      = 5   # Times less than this are displayed in red
midTime        = 10  # Times less than this are displayed yellow

width          = 32  # Matrix size (pixels) -- change for different matrix
height         = 16  # types (incl. tiling).  Other code may need tweaks.
matrix         = Adafruit_RGBmatrix(16, 1) # rows, chain length
fps            = 12  # Scrolling speed (ish)

routeColor     = (255, 255, 255) # Color for route labels (usu. numbers)
descColor      = (110, 110, 110) # " for route direction/description
longTimeColor  = (  0, 255,   0) # Ample arrival time = green
midTimeColor   = (255, 255,   0) # Medium arrival time = yellow
shortTimeColor = (255,   0,   0) # Short arrival time = red
minsColor      = (110, 110, 110) # Commans and 'minutes' labels
noTimesColor   = (  0,   0, 255) # No predictions = blue

# TrueType fonts are a bit too much for the Pi to handle -- slow updates and
# it's hard to get them looking good at small sizes.  A small bitmap version
# of Helvetica Regular taken from X11R6 standard distribution works well:
font           = ImageFont.load(os.path.dirname(os.path.realpath(__file__))
                   + '/helvR08.pil')
fontYoffset    = -2  # Scoot up a couple lines so descenders aren't cropped


# Main application -----------------------------------------------------------

# Drawing takes place in offscreen buffer to prevent flicker
image       = Image.new('RGB', (width, height))
draw        = ImageDraw.Draw(image)
currentTime = 0.0
prevTime    = 0.0

# Clear matrix on exit.  Otherwise it's annoying if you need to break and
# fiddle with some code while LEDs are blinding you.
def clearOnExit():
	matrix.Clear()

atexit.register(clearOnExit)

# Populate a list of predict objects (from predict.py) from stops[].
# While at it, also determine the widest tile width -- the labels
# accompanying each prediction.  The way this is written, they're all the
# same width, whatever the maximum is we figure here.
tileWidth = font.getsize(
  '88' *  maxPredictions    +          # 2 digits for minutes
  ', ' * (maxPredictions-1) +          # comma+space between times
  '')[0]                       # 1 space + 'minutes' at end
w = font.getsize('No Predictions')[0]  # Label when no times are available
if w > tileWidth:                      # If that's wider than the route
	tileWidth = w                  # description, use as tile width.
predictList = []                       # Clear list
for s in stops:                        # For each item in stops[] list...
	predictList.append(predict(s)) # Create object, add to predictList[]
	w = font.getsize(s[1] + ' ' + s[3])[0] # Route label
	if(w > tileWidth):                     # If widest yet,
		tileWidth = w                  # keep it
tileWidth += 6                         # Allow extra space between tiles
time.sleep(5)
while True:
    for prediction in predictList:
        print(prediction.predictions)
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        draw.text((0, -2), text=prediction.data[1] + '', font=font, fill=routeColor)
        times = ','.join([str(sec / 60) for sec in prediction.predictions[0:3]])
        draw.text((0, 6), text=times, font=font, fill=routeColor)
        matrix.SetImage(image.im.id, 0, 0)
        sleep(5)
        matrix.Clear
        # HI AGAIN!!
