# Documentation: Spotify E‑Paper Display with Waveshare UPS HAT (Raspberry Pi Zero)

## Overview
This project runs on a Raspberry Pi Zero with a Waveshare 2.13" tri-color e‑paper display (`epd2in13b_V4`) and a Waveshare UPS HAT for battery power. It shows:
- Current **time** (large font)
- Current **date** (small font)
- Currently playing **Spotify track** (via the Spotify Web API)
- **Battery percentage + icon** (measured from UPS HAT)
- Battery indicator switches to **red if <20%**

Optional: Extend with **charging/discharging status arrows**.

---

## Hardware Requirements
- Raspberry Pi Zero (any model with GPIO/I²C)
- Waveshare 2.13" tri‑color e‑paper display (V4)
- Waveshare UPS HAT (with INA219 power monitor)
- LiPo battery (single cell 3.7 V)

---

## Software Requirements
### Raspberry Pi OS Setup
1. **Enable I²C**:
   ```bash
   sudo raspi-config
   # → Interface Options → I2C → Enable
   sudo reboot
   ```

2. **Install required system packages**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-smbus i2c-tools python3-pip
   ```

3. **Check INA219 detection**:
   ```bash
   i2cdetect -y 1
   ```
   Expected output:
   ```
   40: -- -- -- 43 -- -- -- --
   ```
   The UPS HAT reports as **0x43** (I²C address).

### Python Dependencies
```bash
pip3 install spotipy python-dotenv pi-ina219 pillow
```

Also install Waveshare’s Python driver for `epd2in13b_V4`.

---

## Environment Variables
The Spotify API requires credentials. Create a `.env` file in your project root:
```ini
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

Register your app at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

---

## Key Components in Code

### 1. Spotify Track Fetching
```python
def get_song_title_only():
    track = sp.current_user_playing_track()
    if track and track.get('item') and track.get('is_playing'):
        return track['item']['name']
    return "No music playing"
```
- Uses `spotipy` library with `SpotifyOAuth`.
- Returns current track name, or fallback message.

### 2. Battery Measurement (INA219)
```python
INA219_ADDR = 0x43  # UPS HAT address
def get_battery_level():
    ina = INA219(shunt_ohms=0.1, max_expected_amps=2, address=INA219_ADDR)
    ina.configure()
    voltage = ina.voltage()
    percent = int(((voltage - 3.0) / (4.2 - 3.0)) * 100)
    return max(0, min(100, percent))
```
- Maps LiPo voltage range **3.0–4.2 V → 0–100%**.
- Returns `-1` if measurement fails.

### 3. Battery Icon Drawing
```python
def draw_battery(draw_b, draw_r, x, y, level, font):
    pct_txt = f"{level}%" if level >= 0 else "N/A"
    target = draw_r if (level >= 0 and level < 20) else draw_b
    # Draw rectangle + fill
    # Show % text left of icon
```
- Uses **black layer** for normal, **red layer** for low battery.
- Simple rectangular battery icon with percentage text.

### 4. Screen Update Loop
```python
while True:
    time_txt = strftime("%H:%M", now)
    date_txt = strftime("%a, %d %b %Y", now)
    song_txt = get_song_title_only()
    battery_level = get_battery_level()

    if minute != prev_minute or song_txt != prev_song or battery_level != prev_batt:
        draw_screen(epd, time_txt, date_txt, song_txt, battery_level)
        epd.sleep(); epd.init()

    time.sleep(POLL_SEC)
```
- Updates every minute, or when track/battery changes.
- Uses **full refresh** (required for tri‑color panels).

---

## Power Management
- The script calls `epd.sleep()` between refreshes to save power.
- Re‑initializes before each refresh.
- UPS HAT supplies stable power during sleep/updates.

---

## Possible Extensions
1. **Charging Status**:
   - Use `ina.current()` to detect current direction.
   - Add arrows (`↑` charging, `↓` discharging) next to %.

2. **Improved Battery Estimation**:
   - Replace linear mapping with LiPo discharge curve for better accuracy.
   - Example: 3.7 V is closer to ~50%.

3. **Graphical Enhancements**:
   - Bigger battery icon.
   - Song artist line in red instead of black.
   - Show Wi‑Fi or IP address.

---

## Troubleshooting
- **Shows `N/A` for battery** → Check `i2cdetect -y 1`, confirm `0x43` address.
- **No Spotify data** → Ensure `.env` is correct, token authorized.
- **Ghosting on display** → Full refresh only; tri‑color models don’t support partial refresh.
- **Slow updates** → Increase `POLL_SEC` or update only on minute/track change.

---

## Example Output
```
12:45
Tue, 02 Sep 2025
Track: Shape of You
Battery: 67% [ ██████--- ]
```
If battery <20%:
```
12:45
Tue, 02 Sep 2025
Track: Shape of You
Battery: 18% [ ██------- ]  (red)
```

---

## Conclusion
This project demonstrates how to:
- Combine **Spotify API**, **Waveshare e‑paper**, and **UPS HAT battery monitoring**.
- Display essential info in a **low‑power, always‑on clock/music station**.
- Extend functionality with charging indicators and graphical tweaks.

