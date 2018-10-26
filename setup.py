#!/usr/bin/env python3

from distutils.core import setup

long_description = '''
python-libevdev is a Python wrapper arround the libevdev C library. It
provides a Pythonic API to read events from the Linux kernel's input device
nodes and to read and/or modify the device's state and capabilities.

The documentation is available here:
https://python-evdev.readthedocs.io/en/latest/
'''

setup(name='libevdev',
      version='0.6',
      description='Python wrapper for libevdev',
      long_description=long_description,
      author='Peter Hutterer',
      author_email='peter.hutterer@who-t.net',
      url='https://www.github.com/whot/python-libevdev/',
      packages=['libevdev'],
      classifiers=[
           'Development Status :: 3 - Alpha',
           'Topic :: Software Development',
           'Intended Audience :: Developers',
           'License :: OSI Approved :: MIT License',
           'Programming Language :: Python :: 3',
          ],
      python_requires='>=3',
)
