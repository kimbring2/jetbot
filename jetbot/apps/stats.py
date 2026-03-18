import time

# For Jetson Hardware
from jetbot.utils.utils import get_ip_address
import subprocess

# For scanning I2C bus and SparkFun Hardware
#import qwiic
from jetbot.i2c_scan import get_i2c_address
from jetbot.INA219 import INA219

# For Adafruit Hardware
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont



# Scan for devices on I2C bus
#addresses = qwiic.scan()
addresses = get_i2c_address(7)

# Initialize Display-----------------------------------------------------------
# Try to connect to the OLED display module via I2C.


def reset_display(disp):
	# Initiallize Display
	disp.begin()

	# Clear display.
	disp.clear()
	disp.display()

	# Create blank image for drawing.
	# Make sure to create image with mode '1' for 1-bit color.
	width = disp.width
	height = disp.height
	image = Image.new('1', (width, height))

	# Get drawing object to draw on image.
	draw = ImageDraw.Draw(image)

	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)
	
	return image, draw
	

# 128x32 display (default)---------------------------------------------
if 60 in addresses:
	disp1 = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=7, gpio=1) # setting gpio to 1 is hack to avoid platform detection
	try:
		image, draw = reset_display(disp1)
	except OSError as err:
		print("OS error: {0}".format(err))
		time.sleep(5)


if 65 in addresses:
	print("65 in addresses")
	# Note: Use i2c_bus=7 as confirmed by your i2cdetect scan
	sensor = INA219(address=0x41, i2c_bus=7)
		
	# To use high precision 16V/400mA:
	sensor.set_calibration_16V_400mA()
	
	
previous_voltage = 0
while True:
	# Check Eth0, Wlan0, and Wlan1 Connections---------------------------------
	a = 0    # Indexing of Connections

	# Draw some shapes.
	# First define some constants to allow easy resizing of shapes.
	width = disp1.width
	height = disp1.height
	padding = -2
	top = padding
	bottom = height-padding
	
	# Load default font.
	font = ImageFont.load_default()
	
	# Move left to right keeping track of the current x position for drawing shapes.
	x = 0

	# Checks for Ethernet Connection
	try:
		eth = get_ip_address('eth0')
		if eth != None:
			a = a + 1
	except Exception as e:
		print(e)

	# Checks for WiFi Connection on wlan0
	try:
		wlan0 = get_ip_address('wlP1p1s0')
		if wlan0 != None:
			a = a + 2
	except Exception as e:
			print(e)

	# Checks for WiFi Connection on wlan1
	try:
		wlan1 = get_ip_address('wlan1')
		if wlan1 != None:
			a = a + 4
	except Exception as e:
		print(e)
	
	
	# Check Resource Usage-----------------------------------------------------
	# Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-$
		
	# CPU Load
	cmd = "top -bn1 | grep load | awk '{printf \"%.1f%%\", $(NF-2)}'"
	CPU = subprocess.check_output(cmd, shell = True )
	
	# Memory Use
	cmd = "free -m | awk 'NR==2{printf \"%.1f%%\", $3*100/$2}'"
	Mem_percent = subprocess.check_output(cmd, shell = True )
	cmd = "free -m | awk 'NR==2{printf \"%.2f/%.1f\", $3/1024,$2/1024}'"
	MemUsage = subprocess.check_output(cmd, shell = True )
	
	# Disk Storage
	cmd = "df -h | awk '$NF==\"/\"{printf \"%s\", $5}'"
	Disk_percent = subprocess.check_output(cmd, shell = True )
	cmd = "df -h | awk '$NF==\"/\"{printf \"%d/%d\", $3,$2}'"
	DiskUsage = subprocess.check_output(cmd, shell = True )

	BatteryVoltage = sensor.get_bus_voltage_v()
	BatteryVoltage = round(BatteryVoltage, 2)
	BatteryVoltage = str(BatteryVoltage)
	if previous_voltage != BatteryVoltage:
		image, draw = reset_display(disp1)
		previous_voltage = BatteryVoltage
		#print("BatteryVoltage: ", BatteryVoltage)

	# 128x32 display (default)-------------------------------------------------
	#if 60 in addresses:
	if True:
		# IP address
		if a == 1:
			draw.text((x, top),       "eth0: " + str(eth),  font=font, fill=255)
		elif a == 2:
			draw.text((x, top+0),     "wlan0: " + str(wlan0), font=font, fill=255)
		elif a == 3:
			draw.text((x, top),       "eth0: " + str(eth),  font=font, fill=255)
			draw.text((x, top+0),     "wlan0: " + str(wlan0), font=font, fill=255)
		elif a == 4:
			draw.text((x, top+0),     "wlan1: " + str(wlan1), font=font, fill=255)
		elif a == 5:
			draw.text((x, top),       "eth0: " + str(eth),  font=font, fill=255)
			draw.text((x, top+0),     "wlan1: " + str(wlan1), font=font, fill=255)
		else:
			draw.text((x, top),       "No Connection!",  font=font, fill=255)
		
		# Resource Usage
		draw.text((x, top+8),    "Mem: " + str(MemUsage.decode('utf-8')) + "GB",  font=font, fill=255)
		draw.text((x, top+16),    "Disk: " + str(DiskUsage.decode('utf-8')) + "GB",  font=font, fill=255)
		draw.text((x, top+24),    "Batt: " + BatteryVoltage + "V",  font=font, fill=255)

		# Display image.
		disp1.image(image)
		disp1.display()
		time.sleep(1)
	else:
		break
