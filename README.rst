Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-neopixel_spi/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/neopixel_spi/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI/actions/
    :alt: Build Status

SPI driven CircuitPython driver for NeoPixels.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Pypixelbuf <https://github.com/adafruit/Adafruit_CircuitPython_Pypixelbuf>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-neopixel_spi/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-neopixel-spi

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-neopixel-spi

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-neopixel-spi

Usage Example
=============

.. code-block:: python

    import board
    import neopixel_spi

    pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), 10)
    pixels.fill(0xff0000)

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/neopixel_spi/en/latest/>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
