#!/bin/bash

[[ -d application/vendor/ ]] || mkdir -p application/vendor/
pip install --target application/vendor/ gcloud

# Remove non-App Engine friendly version of pytz.
rm -fr application/vendor/pytz/

wget https://pypi.python.org/packages/source/g/gaepytz/gaepytz-2011h.zip#md5=0f130ef491509775b5ed8c5f62bf66fb
unzip -oq gaepytz-2011h.zip
mv gaepytz-2011h/pytz application/vendor/
rm -fr gaepytz-2011h/
rm -f gaepytz-2011h.zip

git add application/vendor/
