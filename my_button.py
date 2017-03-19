from machine import Pin, Timer
import ds18x20, network, onewire, socket, time, urequests

button = Pin(13, Pin.IN, Pin.PULL_UP)
test_light = Pin(15, Pin.OUT)

time_to_send_temp = False
toggle_light_needed = False
sending_request = False

post_url = 'http://192.168.5.123:8123/api/services/switch/toggle'
post_body = '{"entity_id": "switch.office_lamp_switch_4_0"}'
temp_url = 'http://192.168.5.123:8123/api/states/sensor.office_temp'

def toggle_light_urequests():
    """
    POST request to turn off light
    """
    global toggle_light_needed, sending_request

    sta = network.WLAN(network.STA_IF)
    print(sta.ifconfig())

    sending_request = True
    toggle_light_needed = False
    try:
        r = urequests.request('POST', post_url, post_body)
        _ = r.text
        # print('got response', r.text)
    finally:
        sending_request = False

def button_callback(p):
    global toggle_light_needed
    print('button triggered')
    toggle_light_needed = True

cb = button.irq(trigger=Pin.IRQ_RISING, handler=button_callback)

# keeping line here because connection fails if it's removed
sta = network.WLAN(network.STA_IF)

# Temperature
def get_temp():
    dat = Pin(12)
    ow = onewire.OneWire(dat)
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()
    print('found roms', roms)
    ds.convert_temp()
    time.sleep_ms(750)
    temp = ds.read_temp(roms[0])
    print('temp', temp)
    return temp

def send_temp():
    sta = network.WLAN(network.STA_IF)
    print(sta.ifconfig())

    temp = get_temp()
    url = temp_url
    headers = {'Content-Type': 'application/json'}
    post_body = '{"state": %s, "attributes": {"unit_of_measurement": "C"}}' % (temp)

    try:
        r = urequests.request('POST', url, data=post_body, headers=headers)
        _ = r.text
    except:
        pass

def set_to_send_temp(timer):
    global time_to_send_temp
    time_to_send_temp = True

def loop_forever():
    global x, toggle_light_needed, test_light, time_to_send_temp
    #temp_timer = Timer(-1)
    #temp_timer.init(period=60000, callback=set_to_send_temp)

    while True:
        time.sleep_ms(200)
        # print(toggle_light_needed, time_to_send_temp)
        test_light.value(not test_light.value())

        if toggle_light_needed:
            toggle_light_needed = False
            toggle_light_urequests()

        #if time_to_send_temp:
        #    time_to_send_temp = False
        #    send_temp()
        #    pass

# loop_forever()
