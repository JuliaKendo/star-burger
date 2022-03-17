#!/usr/bin/env bash

set -e

work_folder="/opt/star-burger"
rollbar_token="218fcc9768274497bbb483d548e5b9d2"
rollbar_env="production"

source $work_folder/venv/bin/activate

apt-get -qq -y install httpie> /dev/null

/usr/bin/git -C $work_folder pull --quiet
commit_hash=$(git rev-parse --short HEAD)

http --verify=no POST https://api.rollbar.com/api/1/deploy X-Rollbar-Access-Token:$rollbar_token \
  environment=$rollbar_env \
  revision=$commit_hash \
  local_username=$(logname) \
  status="failed"> /dev/null

yes | pip install -r $work_folder/requirements.txt --quiet

apt-get -qq -y install nodejs> /dev/null
apt-get -qq -y  install npm> /dev/null

npm install -g --silent parcel-bundler@1.12.3> /dev/null
npx browserslist@latest --update-db> /dev/null
parcel build bundles-src/index.js --no-minify -d bundles --public-url="./"> /dev/null

if [ ! -d $work_folder/staticfiles ]; then mkdir $work_folder/staticfiles; fi

if [ $? -ne 0 ]; then
  yes "yes" | python $work_folder/manage.py collectstatic> /dev/null
  yes "yes" | python $work_folder/manage.py migrate foodcartapp> /dev/null
  yes "yes" | python $work_folder/manage.py migrate> /dev/null

  echo "deploy aborted"
  exit
fi

systemctl reload nginx
systemctl restart starburger certbot-renewal.timer starburger-clearsessions.timer

http --verify=no POST https://api.rollbar.com/api/1/deploy X-Rollbar-Access-Token:$rollbar_token \
  environment=$rollbar_env \
  revision=$commit_hash \
  local_username=$(logname) \
  status="succeeded"> /dev/null

deactivate

echo "deploy is finished"
