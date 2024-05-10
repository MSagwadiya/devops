#!/bin/bash

cd $HOME/ptp4l

/usr/sbin/ptp4l -f ptp4l.conf -m >> ptp4l.log 2>&1 &
sleep 5
/usr/sbin/phc2sys -a -r -m -q >> phc2sys.log 2>&1 &
