#!/bin/bash
echo " ~ Sync'ing the Real Time Clock (RTC) with the current Raspberry Pi Time ..."
echo " ~ Verify that the Raspberry Pi is connected to Wifi for proper time sync ..."
echo ""

sudo hwclock --verbose -w

echo " ~ RTC time sync completed!"
echo ""
echo " ~ You may now turn OFF the Raspberry Pi WiFi"
echo ""