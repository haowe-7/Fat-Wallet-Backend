#!/usr/bin/env bash

set -ex
umask 022

apt-get update
apt-get install runit

pip3 install  -i http://mirrors.aliyun.com/pypi/simple \
  --trusted-host mirrors.aliyun.com --no-cache-dir --disable-pip-version-check \
  flask_migrate flask_restful pymysql redis celery

ASSETS_PATH=/tmp/assets

cp ${ASSETS_PATH}/cmd.sh /usr/local/bin/init
chmod a+x /usr/local/bin/init

