import asyncio
import datetime
import struct
from functools import cache

import adafruit_ssd1306
import bitstruct
import board
import digitalio
from bleak import BleakClient
from PIL import Image, ImageDraw, ImageFont


@cache
def init_display():
    i2c = board.I2C()
    return adafruit_ssd1306.SSD1306_I2C(
        128, 64, i2c, addr=0x3C, reset=digitalio.DigitalInOut(board.D4)
    )


def display_bpm(bpm, workout_seconds):
    oled = init_display()

    # image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    draw.text(
        (1, 1),
        f"{bpm:03}",
        font=ImageFont.load_default(size=40),
        fill=255,
    )
    draw.text(
        (128 - 45, 64 - 20),
        f"{int(workout_seconds/60):02}:{(workout_seconds%60):02}",
        font=ImageFont.load_default(size=17),
        fill=255,
    )

    oled.image(image)
    oled.show()


def display_text(text):
    oled = init_display()
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    draw.text(
        (1, 1),
        text,
        font=ImageFont.load_default(size=15),
        fill=255,
    )
    oled.image(image)
    oled.show()


def clear_display():
    oled = init_display()
    oled.fill(0)
    oled.show()


workout_start = None


async def run(address):
    HR_MEAS = "00002A37-0000-1000-8000-00805F9B34FB"

    async with BleakClient(address, timeout=100) as client:
        connected = await client.is_connected()
        display_text(f"connected: {connected}")

        def hr_val_handler(sender, data):
            """Simple notification handler for Heart Rate Measurement."""
            (
                unused,
                rr_int,
                nrg_expnd,
                snsr_cntct_spprtd,
                snsr_detect,
                hr_fmt,
            ) = bitstruct.unpack("b3b1b1b1b1b1", data)
            if hr_fmt:
                (hr_val,) = struct.unpack_from("<H", data, 1)  # uint16
            else:
                (hr_val,) = struct.unpack_from("<B", data, 1)  # uint8

            global workout_start
            if hr_val > 0:
                if not workout_start:
                    workout_start = datetime.datetime.utcnow()
                delta = datetime.datetime.utcnow() - workout_start
                display_bpm(hr_val, delta.seconds)
            else:
                if workout_start:
                    # clear display once after workout
                    clear_display()
                workout_start = None

            # activate for debugging:
            if False:
                print(
                    "HR: {0:3} bpm. Complete raw data: {1} ".format(
                        hr_val, data.hex(sep=":")
                    )
                )

        await client.start_notify(HR_MEAS, hr_val_handler)

        while await client.is_connected():
            await asyncio.sleep(1)


if __name__ == "__main__":
    chest_strap_id = "EB:D4:07:40:52:A0"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(chest_strap_id))
