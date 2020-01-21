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

# The following creates a mock neopixel_write module to allow importing
# the CircuitPython NeoPixel module without actually providing neopixel_write.
#pylint: disable=wrong-import-position, exec-used
import sys
from types import ModuleType
MOCK_MODULE = ModuleType('mock_neopixel_write')
exec('def neopixel_write(): pass', MOCK_MODULE.__dict__)
sys.modules['neopixel_write'] = MOCK_MODULE
#pylint: enable=wrong-import-position, exec-used

from neopixel import NeoPixel

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI.git"

# Pixel color order constants
RGB = 'RGB'
"""Red Green Blue"""
GRB = 'GRB'
"""Green Red Blue"""
RGBW = 'RGBW'
"""Red Green Blue White"""
GRBW = 'GRBW'
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
    #pylint: disable=invalid-name, super-init-not-called, too-many-instance-attributes

    FREQ = 6400000  # 800kHz * 8, actual may be different
    TRST = 80e-6    # Reset code low level time

    def __init__(self, spi, n, *, bpp=3, brightness=1.0, auto_write=True, pixel_order=None):
        # We can't call super().__init__() since we don't actually
        # have a pin to supply it. So setup is done manually.
        #
        # neopixel stuff
        #
        self.bpp = bpp
        self.n = n
        if not pixel_order:
            pixel_order = GRB if bpp == 3 else GRBW
        else:
            self.bpp = bpp = len(pixel_order)
        #
        # pypixelbuf stuff
        #
        bpp, byteorder_tuple, has_white, _ = self.parse_byteorder(pixel_order)
        self._pixels = n
        self._bytes = bpp * n
        self._byteorder = byteorder_tuple
        self._byteorder_string = pixel_order
        self._has_white = has_white
        self._bpp = bpp
        self._bytearray = bytearray(n * bpp)
        self._two_buffers = True
        self._rawbytearray = bytearray(n * bpp)
        self._offset = 0
        self._dotstar_mode = False
        self._pixel_step = bpp
        self.auto_write = False
        self.brightness = min(1.0, max(0, brightness))
        self.auto_write = auto_write
        #
        # neopixel_spi stuff
        #
        from adafruit_bus_device.spi_device import SPIDevice
        self._spi = SPIDevice(spi, baudrate=self.FREQ)
        with self._spi as spibus:
            try:
                # get actual SPI frequency
                freq = spibus.frequency
            except AttributeError:
                # use nominal
                freq = self.FREQ
        self.RESET = bytes([0]*round(freq * self.TRST / 8))
        self.spibuf = bytearray(8 * n * bpp)

    def deinit(self):
        """Blank out the NeoPixels."""
        self.fill(0)
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
