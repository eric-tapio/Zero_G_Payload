#!/bin/bash
echo " ~ Updating Zero G Payload software ..."
echo ""

echo " ~ Before connecting to the software server, verify that Wifi is turned ON ..."
echo " ~ Press any key to continue ..."
read -n 1 -s -r

cd ~/Zero_G_Payload
git pull https://github.com/eric-tapio/Zero_G_Payload.git main

echo ""
echo " ~ Zero G Payload software update Complete!"
echo ""

echo " ~ Wifi may now be turned OFF ..."
echo " ~ Press any key to close this window ..."
read -n 1 -s -r