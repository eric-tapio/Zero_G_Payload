#!/bin/bash

#!/bin/bash
echo ""
echo " ~ Starting Automatic Run of the Zero G Payload Experiment ..."
echo ""

sudo systemctl enable disable_rpi_power_led.service
sudo systemctl start disable_rpi_power_led.service

sudo systemctl enable zero_g_startup.service
sudo systemctl start zero_g_startup.service

echo " ~ Zero G Payload Experiment will automatically start when the unit is powered"
echo " ~ Press any key to close this window ..."
read -n 1 -s -r