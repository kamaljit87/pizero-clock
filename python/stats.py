#!/usr/bin/env python
# encoding: utf-8

 #  @filename   :   main.cpp
 #  @brief      :   2.13inch e-paper display demo
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     September 9 2017
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documnetation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to  whom the Software is
 # furished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 ##
from __future__ import unicode_literals

import epd2in13b_V4
import time
import PIL
import sys
import requests
import logging
from PIL import Image, ImageDraw, ImageFont
from textwrap import dedent
import requests
import subprocess
import json
from time import gmtime, strftime

#api_url = 'http://localhost/admin/api.php'

def deep_reset(epd):
    print ("resetting to white...")
    white_screen = Image.new('1', (epd2in13b_V4.EPD_WIDTH, epd2in13b_V4.EPD_HEIGHT), 255)
    epd.display_frame(epd.getbuffer(white_screen), epd.getbuffer(white_screen))
    epd.delay_ms(1000)

def update(epd):

    # EPD 2 inch 13 b HAT is rotated 90 clockwize and does not support partial update
    # But has amazing 2 colors
    print ("drawing status")
    width = epd2in13b_V4.EPD_HEIGHT
    height = epd2in13b_V4.EPD_WIDTH
    top = 2
    fill_color = 0
    xt = 70
    xc = 120
    xc2 = 164
    ROTATE_0 = 0
    ROTATE_90 = 1
    ROTATE_180 = 2
    ROTATE_270 = 3

    while True:
        frame_black = Image.new('1', (width, height), 255)
        frame_red = Image.new('1', (width, height), 255)

        pihole_logo_top = Image.open('pihole-bw-80-top.bmp')
        pihole_logo_bottom = Image.open('pihole-bw-80-bottom.bmp')
        # pihole_logo = Image.open('monocolo    r.bmp')

        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 11)
        font_bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 12)
        font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 12)
        font_title_bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 12)
        font_debug = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 8)

        # font = ImageFont.truetype('slkscr.ttf', 15)
        draw_black = ImageDraw.Draw(frame_black)

        draw_black.rectangle((0, 0, width, height), outline=0, fill=None)

        ip = subprocess.check_output( "hostname -I | cut -d' ' -f1", shell=True).strip()
        print ("ip:", ip)
        host = subprocess.check_output("hostname", shell=True).strip().decode()
        print ("host:", host)
        mem_usage = subprocess.check_output(dedent("""
        free -m | awk 'NR==2{printf "Mem: %s/%sMB %.2f%%", $3,$2,$3*100/$2 }'
        """).strip(), shell=True).decode().replace("Mem: ", "")
        print ("memory usage:", mem_usage)
        disk = subprocess.check_output(dedent("""
            df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'
            """).strip(), shell=True).decode().replace("Disk: ", "")
        print ("disk:", disk)

        try:
            with open("secrets.txt", "r") as file:
                APP_PASSWORD = file.read().strip()

            # Disable SSL warnings (only for self-signed certs in dev environments)
            requests.packages.urllib3.disable_warnings()

        # Step 1: Authenticate and get session SID
            auth_response = requests.post(
            "http://localhost/api/auth",
            json={"password": APP_PASSWORD},
            verify=False
            )

            sid = auth_response.json().get("session", {}).get("sid")

            if sid:
                # Step 2: Get stats summary
                stats_response = requests.get(
                f"http://localhost/api/stats/summary?sid={sid}",
                verify=False
                )
                stats_data = stats_response.json()

                # Step 3: Extract desired values
                blocked = stats_data.get("blocked")
                active_clients = stats_data.get("clients", {}).get("active")
                total_queries = stats_data.get("queries", {}).get("total")

                # Print or use the variables
                print(f"Blocked domains: {blocked}")
                print(f"Active clients: {active_clients}")
                print(f"Total queries: {total_queries}")

                # Step 4: Logout
                logout_response = requests.delete(
                f"http://localhost/api/auth?sid={sid}",
                verify=False
                )
            else:
                print("Authentication failed. Check password or API URL.")
        except KeyError:
            time.sleep(1)
           # continue

        frame_black.paste(pihole_logo_top, (-8, 2))
        frame_red.paste(pihole_logo_bottom, (-8, 2))
        draw_red = ImageDraw.Draw(frame_red)
        draw_red.text((10, height - 21), "Pi", font=font_title_bold, fill=fill_color)
        draw_red.text((23, height - 21), "-hole", font=font_title_bold, fill=fill_color)

        draw_black.text((xt, top + 0), "HOST: ", font=font_bold, fill=fill_color)
        draw_black.text((xc, top + 0), host, font=font, fill=fill_color)
        draw_black.text((xt, top + 15), "IP: ", font=font_bold, fill=fill_color)
        draw_black.text((xc, top + 15), str(ip), font=font, fill=fill_color)
        draw_black.text((xt, top + 30), "Mem:",  font=font_bold, fill=fill_color)
        draw_black.text((xc, top + 30), str(mem_usage),  font=font, fill=fill_color)
        draw_black.text((xt, top + 45), "Disk:",  font=font_bold, fill=fill_color)
        draw_black.text((xc, top + 45),  str(disk),  font=font, fill=fill_color)
        draw_black.text((xt, top + 60), "Ads Blocked: ", font=font_bold, fill=fill_color)
        draw_black.text((xc2, top + 60), str(blocked), font=font, fill=fill_color)
        draw_black.text((xt, top + 75), "Clients:", font=font_bold, fill=fill_color)
        draw_black.text((xc2, top + 75), str(active_clients), font=font, fill=fill_color)
        draw_black.text((xt, top + 90), "DNS Queries: ", font=font_bold, fill=fill_color)
        draw_black.text((xc2, top + 90), str(total_queries), font=font, fill=fill_color)

        draw_black.text((14, height - 10), u"↻: ", font=font, fill=fill_color)
        draw_black.text((24, height - 8), strftime("%H:%M", gmtime()), font=font_debug, fill=fill_color)


        
        epd.display(epd.getbuffer(frame_black.transpose(Image.ROTATE_90)),epd.getbuffer(frame_red.transpose(Image.ROTATE_90)))

        sleep_sec = 1 * 1
        print ("sleeping {0} sec ({1} min) at {1}".format(sleep_sec, sleep_sec / 60,
                                                         strftime("%H:%M", gmtime())))
        epd.sleep()
        time.sleep(sleep_sec * 1000)
        # awakening the display
        epd.init()

def main():
    print ("initing screen...")
    epd = epd2in13b_V4.EPD()
    epd.init()
    epd.Clear()
    try:
        update(epd)
    finally:
        print ("sleeping epd before leaving")
        epd.sleep()

if __name__ == '__main__':
    main()
