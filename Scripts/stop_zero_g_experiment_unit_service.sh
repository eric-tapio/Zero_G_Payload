#!/bin/bash
echo ""
echo " ~ Stopping Automatic Run of the Zero G Payload Experiment ..."
echo ""

sudo systemctl stop zero_g_startup.service

echo " ~ Stopped! The Zero G Payload Experiment may now be run manually."
echo " ~ Press any key to close this window ..."
read -n 1 -s -r