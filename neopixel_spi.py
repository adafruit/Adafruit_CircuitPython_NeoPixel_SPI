# The MIT License (MIT)
#
# Copyright (c) 2019 Carter Nelson for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`neopixel_spi`
================================================================================

SPI driven CircuitPython driver for NeoPixels.


* Author(s): Carter Nelson

Implementation Notes
--------------------

**Hardware:**

* Hardware SPI port required on host platform.

**Software and Dependencies:**

* Adafruit Blinka:
  https://github.com/adafruit/Adafruit_Blinka

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

from neopixel import NeoPixel

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI.git"

# Pixel color order constants
RGB = (0, 1, 2)
"""Red Green Blue"""
GRB = (1, 0, 2)
"""Green Red Blue"""
RGBW = (0, 1, 2, 3)
"""Red Green Blue White"""
GRBW = (1, 0, 2, 3)
"""Green Red Blue White"""

class NeoPixel_SPI(NeoPixel):
    """
    A sequence of neopixels.

    :param ~busio.SPI spi: The SPI bus to output neopixel data on.
    :param int n: The number of neopixels in the chain
    :param int bpp: Bytes per pixel. 3 for RGB and 4 for RGBW pixels.
    :param float brightness: Brightness of the pixels between 0.0 and 1.0 where 1.0 is full
      brightness
    :param bool auto_write: True if the neopixels should immediately change when set. If False,
      `show` must be called explicitly.
    :param tuple pixel_order: Set the pixel color channel order. GRBW is set by default.

    Example:

    .. code-block:: python

        import board
        import neopixel_spi

        pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), 10)
        pixels.fill(0xff0000)
    """
    #pylint: disable=invalid-name, super-init-not-called

    FREQ = 6400000  # 800kHz * 8, actual may be different
    TRST = 80e-6    # Reset code low level time

    def __init__(self, spi, n, *, bpp=3, brightness=1.0, auto_write=True, pixel_order=None):
        from adafruit_bus_device.spi_device import SPIDevice
        self._spi = SPIDevice(spi, baudrate=self.FREQ)
        with self._spi as spibus:
            try:
                # get actual SPI frequency
                freq = spibus.frequency
            except AttributeError:
                # use nominal
                freq = self.FREQ
        self.RESET = bytes([0]*round(freq*self.TRST))
        self.n = n
        if pixel_order is None:
            self.order = GRBW
            self.bpp = bpp
        else:
            self.order = pixel_order
            self.bpp = len(self.order)
        self.buf = bytearray(self.n * self.bpp)
        self.spibuf = bytearray(8*len(self.buf))
        # Set auto_write to False temporarily so brightness setter does _not_
        # call show() while in __init__.
        self.auto_write = False
        self.brightness = brightness
        self.auto_write = auto_write

    def deinit(self):
        """Blank out the NeoPixels."""
        for i in range(len(self.buf)):
            self.buf[i] = 0
        self.show()

    def show(self):
        """Shows the new colors on the pixels themselves if they haven't already
        been autowritten."""
        self._transmogrify()
        #pylint: disable=no-member
        with self._spi as spi:
            # write out special byte sequence surrounded by RESET
            # leading RESET needed for cases where MOSI rests HI
            spi.write(self.RESET + self.spibuf + self.RESET)

    def _transmogrify(self):
        """Turn every BIT of buf into a special BYTE pattern."""
        k = 0
        for byte in self.buf:
            byte = int(byte * self.brightness)
            # MSB first
            for i in range(7, -1, -1):
                if byte >> i & 0x01:
                    self.spibuf[k] = 0b11110000 # A NeoPixel 1 bit
                else:
                    self.spibuf[k] = 0b11000000 # A NeoPixel 0 bit
                k += 1
