#!/usr/bin/env python
# encoding: utf-8

import epd2in13b_V4
import time
from PIL import Image, ImageDraw, ImageFont
from time import gmtime, strftime


def deep_reset(epd):
    print("Resetting to white...")
    white_screen = Image.new('1', (epd2in13b_V4.EPD_WIDTH, epd2in13b_V4.EPD_HEIGHT), 255)
    epd.display_frame(epd.getbuffer(white_screen), epd.getbuffer(white_screen))
    epd.delay_ms(1000)


def update(epd):
    # Screen rotated 90° clockwise for this display
    width = epd2in13b_V4.EPD_HEIGHT
    height = epd2in13b_V4.EPD_WIDTH

    # Fonts
    font_time = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 42)
    font_date = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 16)

    while True:
        frame_black = Image.new('1', (width, height), 255)
        frame_red = Image.new('1', (width, height), 255)

        draw_black = ImageDraw.Draw(frame_black)

        # Get current time & date
        current_time = strftime("%H:%M", gmtime())
        current_date = strftime("%a, %d %b %Y", gmtime())

        # Center time text
        w_time, h_time = draw_black.textsize(current_time, font=font_time)
        w_date, h_date = draw_black.textsize(current_date, font=font_date)

        x_time = (width - w_time) // 2
        y_time = (height // 2) - h_time

        x_date = (width - w_date) // 2
        y_date = y_time + h_time + 10

        # Draw time & date
        draw_black.text((x_time, y_time), current_time, font=font_time, fill=0)
        draw_black.text((x_date, y_date), current_date, font=font_date, fill=0)

        # Push to display
        epd.display(
            epd.getbuffer(frame_black.transpose(Image.ROTATE_180)),
            epd.getbuffer(frame_red.transpose(Image.ROTATE_180))
        )

        # Sleep for 60 sec then refresh
        sleep_sec = 60
        print("Sleeping {} sec...".format(sleep_sec))
        epd.sleep()
        time.sleep(sleep_sec)
        epd.init()


def main():
    print("Initializing screen...")
    epd = epd2in13b_V4.EPD()
    epd.init()
    epd.Clear()
    try:
        update(epd)
    finally:
        print("Putting display to sleep before exit")
        epd.sleep()


if __name__ == '__main__':
    main()

