#!/bin/bash
sudo systemctl enable disable_rpi_power_led.service
sudo systemctl start disable_rpi_power_led.service

sudo systemctl enable zero_g_startup.service
sudo systemctl start zero_g_startup.service