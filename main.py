import my_button, private
import network

def connect():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(private.ssid, private.password)
    sta.ifconfig()

connect()

my_button.loop_forever()

