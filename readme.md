## Heartrate display

using a Chest strap, a PI zero 2 and an i2c-display

blog post: <https://madflex.de/raspberrypi-bluetooth-heart-rate-display/>

### Parts

- PI zero 2 with Raspberry Pi OS installed
- i2c display -- I use <https://www.berrybase.de/0.96-128x64-oled-display-modul-zweifarbig-gelb/blau-spi/i2c-interface-vertikale-stiftleiste>
- Chest strap -- I use a Wahoo TIKR - but every other BLE strap should work

### install

activate i2c
```
raspi-config    # -> enable i2c
```

System packages:
```
# for i2c
apt install i2c-tools
# for pillow
sudo apt-get install libopenjp2-7
```

Python packages:
```
python -m venv venv
. venv/bin/activate
# for ble
pip install dbus-fast bleak bitstruct
# for the display
pip install adafruit-circuitpython-ssd1306 pillow RPi.GPIO
```

Set the BLE Address in ``ble-display.py`` and copy the file to ``/home/pi``.

systemd:
```
sudo cp ble-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ble-display
```
