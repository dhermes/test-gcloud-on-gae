# H/T: www.simonmweber.com/2013/06/18/python-protobuf-on-app-engine.html

import os
import sys

# App Engine imports are higher up the import path.
import google

# Add vendor/google/ to google namespace package so that
# google.protobuf is imported.
curr_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(curr_dir, 'vendor')
google.__path__.append(os.path.join(vendor_dir, 'google'))

# Add vendor path for imports.
sys.path.insert(0, vendor_dir)
