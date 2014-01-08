# Davis Vantage VUE data parser for the Weather Underground API
#Copyright (C) 2013 Brad Boegler
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


# Note offsets start at 1, 0=1, 1=2, etc
# API doc: http://www.davisnet.com/support/weather/download
# /VantageSerialProtocolDocs_v250.pdf
# Brad Boegler 02/24/13 http://bradthx.blogspot.com

from array import array
from sys import exit

#convert string to hex
def hex_to_integer(h):
    """Convert a hex string to an integer.
    The hex string can be any length. It can start with an 0x, or not.
    Unrecognized characters will raise a ValueError.
    This function released into the public domain by it's author, Lion
    Kimbro.
    """
    num = 0  # Resulting integer
    h = h.lower()  # Hex string
    if h[:2] == "0x":
        h = h[2:]
    for c in h:  # Hex character
        num *= 16
        if "0" <= c <= "9":
            num += ord(c) - ord("0")
        elif "a" <= c <= "f":
            num += ord(c) - ord("a") + 10
        else:
            raise ValueError(c)
    return num


crc_table = (
0x0, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
0x1231, 0x210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
0x2462, 0x3443, 0x420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
0x3653, 0x2672, 0x1611, 0x630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
0x48c4, 0x58e5, 0x6886, 0x78a7, 0x840, 0x1861, 0x2802, 0x3823,
0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0xa50, 0x3a33, 0x2a12,
0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0xc60, 0x1c41,
0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0xe70,
0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
0x1080, 0xa1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
0x2b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
0x34e2, 0x24c3, 0x14a0, 0x481, 0x7466, 0x6447, 0x5424, 0x4405,
0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
0x26d3, 0x36f2, 0x691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x8e1, 0x3882, 0x28a3,
0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
0x4a75, 0x5a54, 0x6a37, 0x7a16, 0xaf1, 0x1ad0, 0x2ab3, 0x3a92,
0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0xcc1,
0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0xed1, 0x1ef0,
)

def check_crc(data):
    crc = 0
    for byte in array('B',data):
        crc = (crc_table[ ( crc >> 8 ) ^ byte ] ^ ( ( crc&0xFF ) << 8 ) )
    return crc





print "Start Run"

from decimal import *
import serial 
import time
import urllib2, urllib
import datetime

ser = serial.Serial("/dev/ttyS0", 19200, timeout=1)

print "Get Data"
ser.write("LPS 2 1\n")
	
s = ser.read(100) 
print len(s)

ser.close()

#Test string for received data, 'LOO' should be visible
loop = s[1:4]
#Loop type, VUE uses type 1
loopType = s[5]

#Barometric pressure trend (may not be supported on VUE?)
barTrend = s[4] 

#Current barometric pressure, two bytes (swapped) 
curBarLowByte = s[8]
curBarHighByte = s[9]
curBar = curBarHighByte + curBarLowByte
curBar = curBar.encode('hex')
curBar = hex_to_integer(curBar)
curBar = Decimal(curBar) / Decimal('1000.00')

#Outside humidity, one byte, direct percent
outsideHum = s[34]
outsideHum = ord(outsideHum)

#Outside temperature, two bytes (swapped)
outsideTempLowByte = s[13]
outsideTempHighByte = s[14]
outsideTemp = outsideTempHighByte + outsideTempLowByte
outsideTemp = outsideTemp.encode('hex')
outsideTemp = hex_to_integer(outsideTemp)
outsideTemp = Decimal(outsideTemp) / Decimal('10')
#outsideTemp = Decimal('130.0')a # FOR TESTING 
if outsideTemp > 1000:
	outsideTemp = outsideTemp - 6553

#Wind Speed, one byte unsigned direct value in mph
windSpeed = s[15]
windSpeed = ord(windSpeed)

#Wind direction, two byte conversion (swapped)
windDirLowByte = s[17]
windDirHighByte = s[18]
windDir = windDirHighByte + windDirLowByte
windDir = windDir.encode('hex')
windDir = hex_to_integer(windDir)

#Get UTC time in wunderground format YYYY-MM-DD HH:MM:SS
utc_datetime = datetime.datetime.utcnow()
utcTime = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")

#Get dewpoint, two bytes (swapped) displays in degrees f

dewPointLowByte = s[31]
dewPointHighByte = s[32]
dewPoint = dewPointHighByte + dewPointLowByte
dewPoint = dewPoint.encode('hex')
dewPoint = hex_to_integer(dewPoint)
dewPoint = Decimal(dewPoint)
if dewPoint > 1000:
	dewPoint = dewPoint - 65535


#Wind Gust 10 min resolution, two byte val .1 resolution

windGustLowByte = s[23]
windGustHighByte = s[24]
windGust = windGustHighByte + windGustLowByte
windGust = windGust.encode('hex')
windGust = hex_to_integer(windGust)
windGust = Decimal(windGust)

#Rainfall in inches over last hour. Two bytes (swapped)
rainHourlyLowByte = s[55]
rainHourlyHighByte = s[56]
rainHourly = rainHourlyHighByte + rainHourlyLowByte
rainHourly = rainHourly.encode('hex')
rainHourly = hex_to_integer(rainHourly)
rainHourly = Decimal(rainHourly) / Decimal('100')

#Rainfall daily (day based on local time) Two bytes, swapped
rainDailyLowByte= s[51]
rainDailyHighByte = s[52]
rainDaily = rainDailyHighByte + rainDailyLowByte
rainDaily = rainDaily.encode('hex')
rainDaily = hex_to_integer(rainDaily)
rainDaily = Decimal(rainDaily) / Decimal('100')

#Print converted data

#CRC check
crc_flag = 0
crc_flag = check_crc(s[1:100])

#CRC should always be zero


print "Outside Temp        : %.2f" % outsideTemp
print "Outside Humidity    : %d" % outsideHum
print "Barometric Pressure : %.2f" % curBar
print "Wind Speed          : %d" % windSpeed
print "10 Minute Wind Gust : %.2f" % windGust
print "Wind Direction      : %d" % windDir
print "Dew Point           : %.2f" % dewPoint
print "Hourly rain (in)    : %.2f" % rainHourly
print "Daily rain (in)     : %.2f" % rainDaily
print "UTC Time            : %s" % utcTime
print "CRC Check           : %d" % crc_flag
#Url to wunderground

utcTime = urllib.quote(utcTime)


wunderUrl = ('http://rtupdate.wunderground.com/weatherstation/updateweatherstation.php?ID=<station_id>&PASSWORD=<api-password>&dateutc=') + str(utcTime) + ('&tempf=')+ str(outsideTemp) + ('&humidity=')+ str(outsideHum) + ('&baromin=')+ str(curBar) + ('&winddir=')+ str(windDir) +('&windspeedmph=')+ str(windSpeed) + ('&windgustmph=') + str(windGust) + ('&dewptf=') + str(dewPoint) +('&rainin=') + str(rainHourly) + ('&dailyrainin=') + str(rainDaily) +('&&realtime=1&rtfreq=10')

if crc_flag != Decimal(0) or outsideTemp > Decimal('120') or windGust > Decimal('100') or outsideHum > 101 or windSpeed > 100 or rainHourly > Decimal('3') or rainDaily > Decimal('10'):
    print "NOT_OK - No Upload "
else:
    print "OK - Data Uploaded"
    result = urllib2.urlopen(wunderUrl)


print wunderUrl




