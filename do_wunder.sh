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

# Update path to where your send_wunder.py lives and run this script
# as a cron every minute. It will upload data to the Wunderground
# rapidfire servers every 10 seconds.
# API doc: http://www.davisnet.com/support/weather/download
# /VantageSerialProtocolDocs_v250.pdf
# Brad Boegler 02/24/13 http://bradthx.blogspot.com



(/usr/bin/python /send_wunder.py >> /var/log/wunder.log)&
(sleep 10 && /usr/bin/python /send_wunder.py >> /var/log/wunder.log)&
(sleep 20 && /usr/bin/python /send_wunder.py >> /var/log/wunder.log)&
(sleep 30 && /usr/bin/python /send_wunder.py >> /var/log/wunder.log)&
(sleep 40 && /usr/bin/python /send_wunder.py >> /var/log/wunder.log)&
(sleep 50 && /usr/bin/python /send_wunder.py >> /var/log/wunder.log)&


