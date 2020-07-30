# raspi-cec-commander
Remote control raspi via HDMI-CEC

### HDMI-CEC

https://github.com/Pulse-Eight/libcec/blob/master/docs/README.raspberrypi.md

### Raspi control 

https://pyautogui.readthedocs.io

### Decode HDMI-CEC commands

https://www.cec-o-matic.com/

### Smooth tutorial

(german) https://www.raspberry-pi-geek.de/ausgaben/rpg/2018/12/per-cec-software-auf-dem-raspi-steuern

### Example system service

```
[Unit]
Description=Runs HDMI CEC commander python script
After=multi-user.target

[Service]
User=pi
Type=simple
ExecStart=/home/pi/cec-commander/run.sh

[Install]
WantedBy=multi-user.target
```
