echo 0 > /sys/devices/system/cpu/cpuquiet/tegra_cpuquiet/enable
echo 1 > /sys/devices/system/cpu/cpu0/online
echo 1 > /sys/devices/system/cpu/cpu1/online
echo 1 > /sys/devices/system/cpu/cpu2/online
echo 1 > /sys/devices/system/cpu/cpu3/online
echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo 852000000 > /sys/kernel/debug/clock/override.gbus/rate
echo 1 > /sys/kernel/debug/clock/override.gbus/state

echo -1 > /sys/bus/usb/devices/1-3/power/autosuspend
echo -1 > /sys/bus/usb/devices/2-1/power/autosuspend
echo -1 > /sys/bus/usb/devices/2-1.1/power/autosuspend
echo -1 > /sys/module/usbcore/parameters/autosuspend