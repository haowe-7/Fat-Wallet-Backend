#!/usr/bin/env bash

FILES=`find /etc/service/ -name run`

if [ "${FILES}" ]; then
  chmod a+x ${FILES}
fi

exec /usr/bin/runsvdir -P /etc/service