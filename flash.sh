#!/bin/bash

esptool.py --chip esp32s3 --port $1 erase_flash 
esptool.py --chip esp32s3 --port $1 write_flash -z 0 GENERIC_S3-20220618-v1.19.1.bin
ampy --port $1 --baud 115200 put webrepl_cfg.py
echo "copied webrepl" 
ampy --port $1 --baud 115200 put mlx90615.py 
echo "copied temp"
ampy --port $1 --baud 115200 put ble_advertising.py 
echo "copied BLE"

echo "m$2" > name.txt
ampy --port $1 --baud 115200 put name.txt
echo "copied name"
ampy --port $1 --baud 115200 put main.py
echo "copied main"
echo "Done."


