# H/T: www.simonmweber.com/2013/06/18/python-protobuf-on-app-engine.html

import os

import darth
# App Engine imports are higher up the import path.
import google

darth.vendor('vendor')

# Add vendor/google/ to google namespace package so that
# google.protobuf is imported.
curr_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(curr_dir, 'vendor')
google.__path__.append(os.path.join(vendor_dir, 'google'))
