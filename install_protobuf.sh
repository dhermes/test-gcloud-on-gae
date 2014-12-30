#!/bin/bash

virtualenv protobuf
source protobuf/bin/activate
pip install protobuf
cp -r protobuf/lib/python2.7/site-packages/google/ application/
deactivate
rm -fr protobuf/
git add application/google/
