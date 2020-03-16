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

from adafruit_bus_device.spi_device import SPIDevice
from adafruit_pypixelbuf import PixelBuf, fill

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI.git"

# Pixel color order constants
RGB = "RGB"
"""Red Green Blue"""
GRB = "GRB"
"""Green Red Blue"""
RGBW = "RGBW"
"""Red Green Blue White"""
GRBW = "GRBW"
"""Green Red Blue White"""


class NeoPixel_SPI(PixelBuf):
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

    FREQ = 6400000  # 800kHz * 8, actual may be different
    TRST = 80e-6  # Reset code low level time

    def __init__(
        self, spi, n, *, bpp=3, brightness=1.0, auto_write=True, pixel_order=None
    ):

        # configure bpp and pixel_order
        if not pixel_order:
            pixel_order = GRB if bpp == 3 else GRBW
        else:
            bpp = len(pixel_order)

        # set up SPI related stuff
        self._spi = SPIDevice(spi, baudrate=self.FREQ)
        with self._spi as spibus:
            try:
                # get actual SPI frequency
                freq = spibus.frequency
            except AttributeError:
                # use nominal
                freq = self.FREQ
        self._reset = bytes([0] * round(freq * self.TRST / 8))
        self.spibuf = bytearray(8 * n * bpp)

        # everything else taken care of by base class
        super().__init__(
            n,
            bytearray(n * bpp),
            brightness=brightness,
            rawbuf=bytearray(n * bpp),
            byteorder=pixel_order,
            auto_write=auto_write,
        )

    def deinit(self):
        """Blank out the NeoPixels."""
        self.fill(0)
        self.show()

    def show(self):
        """Shows the new colors on the pixels themselves if they haven't already
        been autowritten."""
        self._transmogrify()
        # pylint: disable=no-member
        with self._spi as spi:
            # write out special byte sequence surrounded by RESET
            # leading RESET needed for cases where MOSI rests HI
            spi.write(self._reset + self.spibuf + self._reset)

    def _transmogrify(self):
        """Turn every BIT of buf into a special BYTE pattern."""
        k = 0
        for byte in self.buf:
            byte = int(byte * self.brightness)
            # MSB first
            for i in range(7, -1, -1):
                if byte >> i & 0x01:
                    self.spibuf[k] = 0b11110000  # A NeoPixel 1 bit
                else:
                    self.spibuf[k] = 0b11000000  # A NeoPixel 0 bit
                k += 1

    def fill(self, color):
        """Colors all pixels the given ***color***."""
        fill(self, color)
