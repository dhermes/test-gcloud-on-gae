#!/bin/bash

virtualenv protobuf
source protobuf/bin/activate
pip install protobuf
mkdir application/vendor/
cp -r protobuf/lib/python2.7/site-packages/google/ application/vendor/
deactivate
rm -fr protobuf/
git add application/google/
