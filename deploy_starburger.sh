#!/bin/bash

work_folder="/opt/star-burger"

/usr/bin/git -C $work_folder pull --quiet

yes | /usr/bin/pip3 install -r $work_folder/requirements.txt --quiet

apt-get -qq -y install nodejs> /dev/null
apt-get -qq -y  install npm> /dev/null

npm install -g --silent parcel-bundler@1.12.3> /dev/null
parcel build bundles-src/index.js -d bundles --public-url="./"> /dev/null

/usr/bin/python3 $work_folder/manage.py collectstatic --noinput> /dev/null
yes "yes" | /usr/bin/python3 $work_folder/manage.py migrate> /dev/null

systemctl restart starburger
systemctl restart certbot-renewal
systemctl reload nginx

echo "deploy is finished"
