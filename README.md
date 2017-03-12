# A button for my light

Home Assistant article:
https://home-assistant.io/blog/2016/07/28/esp8266-and-micropython-part1/

Board Layout

http://www.hotmcu.com/nodemcu-lua-wifi-board-based-on-esp8266-cp2102-module-p-265.html

## Firmware

Downlaod from: http://micropython.org/download#esp8266

## Virtual Env

```
pyvenv venv
source  venv/bin/activate
pip install -r requirements.txt
```

## Upload Firmware

```
esptool.py --port /dev/cu.SLAB_USBtoUART erase_flash
esptool.py --port /dev/cu.SLAB_USBtoUART --baud 460800 write_flash --flash_size=detect 0 esp8266-20170108-v1.8.7.bin
```

## Connect over screen

```
screen /dev/cu.SLAB_USBtoUART 115200
```


## Connect to WiFi

```
import network
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect('ssid', 'password')
sta.ifconfig()
('192.168.x.x', '255.255.255.0', '192.168.x.x', 'dns.ip.x.x')
```

## Get a WebREPL interface

In browser: http://micropython.org/webrepl/

in the screen session:

```
import webrepl_setup
```

## REPL

```
Ctrl-E for paste mode
Ctrl-D on a blank line will do a soft reset.
```



