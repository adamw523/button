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



