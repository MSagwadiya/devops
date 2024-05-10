#!/bin/bash 

chmod go+rw /dev/exanic0 /dev/exasock /dev/exanic1

echo -1 > /proc/sys/kernel/sched_rt_runtime_us
echo 0 > /proc/sys/kernel/watchdog
echo 0 > /proc/sys/kernel/nmi_watchdog
echo 300 > /proc/irq/default_smp_affinity
echo 300 > /sys/bus/workqueue/devices/writeback/cpumask

for i in `ls -d /proc/irq/*`; do echo 300 > $i/smp_affinity; done
for i in {0,1,2,3,4,5,6,7}; do echo 0 >/sys/devices/system/machinecheck/machinecheck$i/check_interval; done
