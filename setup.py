#!/usr/bin/env python3

from distutils.core import setup

setup(name='libevdev',
      version='0.4',
      description='Python wrapper for libevdev',
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
