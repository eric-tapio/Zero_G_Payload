#!/bin/bash
echo " ~ Sync'ing the Real Time Clock (RTC) with the current Raspberry Pi Time ..."
echo ""
echo " ~ Before connecting to the time server, verify that Wifi is turned ON ..."
echo " ~ Press any key to continue ..."
read -n 1 -s -r

echo ""
sudo hwclock --verbose -w
echo ""

echo " ~ RTC time sync completed!"
echo ""
echo " ~ Wifi may now be turned OFF ..."
echo " ~ Press any key to close this window ..."
read -n 1 -s -r
