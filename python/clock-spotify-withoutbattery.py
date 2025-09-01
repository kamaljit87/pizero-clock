#!/usr/bin/env python3
import os
import time
from time import localtime, strftime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import epd2in13b_V4
from PIL import Image as PILImage

# ---------- Config ----------
# Update cadence
POLL_SEC = 5          # how often we poll Spotify/time
ROTATE = 180          # display rotation
# Fonts (adjust sizes to taste)
FONT_TIME_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_TEXT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_TIME_SIZE = 40
FONT_DATE_SIZE = 16
FONT_SONG_SIZE = 14

# ---------- Spotify auth ----------
load_dotenv()  # reads .env
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-currently-playing"
))

def get_song_title_only():
    """Return only the current song title (no artist)."""
    try:
        track = sp.current_user_playing_track()
        if track and track.get('item') and track.get('is_playing'):
            return track['item']['name'] or "Unknown track"
        # If nothing is playing, fall back to last track name if present
        if track and track.get('item'):
            return track['item']['name'] or "No music playing"
        return "No music playing"
    except Exception as e:
        print("Spotify error:", e)
        return "Spotify unavailable"

# ---------- E-paper helpers ----------
def draw_screen(epd, time_txt, date_txt, song_txt):
    """
    Tri-color panel: build black & red frames, then full refresh.
    We’ll keep everything in black for clarity; switch song to red by drawing on frame_red.
    """
    # Dimensions for tri-color driver (note the swap width/height convention)
    width = epd2in13b_V4.EPD_HEIGHT
    height = epd2in13b_V4.EPD_WIDTH

    frame_black = PILImage.new('1', (width, height), 255)  # white background
    frame_red   = PILImage.new('1', (width, height), 255)

    draw_b = ImageDraw.Draw(frame_black)
    draw_r = ImageDraw.Draw(frame_red)

    font_time = ImageFont.truetype(FONT_TIME_PATH, FONT_TIME_SIZE)
    font_date = ImageFont.truetype(FONT_TEXT_PATH, FONT_DATE_SIZE)
    font_song = ImageFont.truetype(FONT_TEXT_PATH, FONT_SONG_SIZE)

    # Measure text to center
    w_time, h_time = draw_b.textsize(time_txt, font=font_time)
    w_date, h_date = draw_b.textsize(date_txt, font=font_date)
    w_song, h_song = draw_b.textsize(song_txt, font=font_song)

    x_time = (width - w_time) // 2
    y_time = (height // 2) - h_time

    x_date = (width - w_date) // 2
    y_date = y_time + h_time + 10

    x_song = (width - w_song) // 2
    y_song = y_date + h_date + 10

    # Draw in black (set song in red if you want it to pop: draw on draw_r instead)
    draw_b.text((x_time, y_time), time_txt, font=font_time, fill=0)
    draw_b.text((x_date, y_date), date_txt, font=font_date, fill=0)
    draw_b.text((x_song, y_song), song_txt, font=font_song, fill=0)
    # Example to make song red, comment the black line above and uncomment below:
    # draw_r.text((x_song, y_song), song_txt, font=font_song, fill=0)

    # Apply rotation
    if ROTATE == 180:
        frame_black = frame_black.transpose(PILImage.ROTATE_180)
        frame_red   = frame_red.transpose(PILImage.ROTATE_180)
    elif ROTATE == 90:
        frame_black = frame_black.transpose(PILImage.ROTATE_90)
        frame_red   = frame_red.transpose(PILImage.ROTATE_90)
    elif ROTATE == 270:
        frame_black = frame_black.transpose(PILImage.ROTATE_270)
        frame_red   = frame_red.transpose(PILImage.ROTATE_270)

    # Send both layers (full update; tri-color panels don’t support partial)
    epd.display(epd.getbuffer(frame_black), epd.getbuffer(frame_red))

def main():
    print("Initializing screen...")
    epd = epd2in13b_V4.EPD()
    epd.init()
    epd.Clear()  # one clean full-clear at start

    prev_minute = None
    prev_song = None

    try:
        while True:
            now = localtime()
            time_txt = strftime("%H:%M", now)          # big clock (no seconds = less churn)
            date_txt = strftime("%a, %d %b %Y", now)   # small date
            song_txt = get_song_title_only()           # title only

            minute = now.tm_min

            # Refresh only if something changed
            if minute != prev_minute or song_txt != prev_song:
                print(f"Update @ {strftime('%H:%M:%S', now)} | song: {song_txt}")
                draw_screen(epd, time_txt, date_txt, song_txt)
                prev_minute = minute
                prev_song = song_txt
                # Put panel to sleep between updates to save power
                epd.sleep()
                # Re-init right before next potential update to keep things simple
                epd.init()

            time.sleep(POLL_SEC)

    except KeyboardInterrupt:
        print("Exiting, putting display to sleep.")
        epd.sleep()

if __name__ == "__main__":
    main()

