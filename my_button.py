from machine import freq, Pin, Timer
import ds18x20, network, onewire, socket, sys, time, urequests
import private

time_to_send_temp = False
toggle_light_needed = False
sending_request = False

post_url = 'http://192.168.5.123:8123/api/services/switch/toggle'
post_body = '{"entity_id": "switch.__switch_4_0"}'
temp_url = 'http://192.168.5.123:8123/api/states/sensor.office_temp'

class WifiConnection(object):
    def __init__(self):
        self.connect()

    def connect(self):
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        sta.connect(private.ssid, private.password)
        sta.ifconfig()

class TestLight(object):
    def __init__(self):
        self.light = Pin(15, Pin.OUT)

    def toggle(self):
        self.light.value(not self.light.value())

    def blink_on(self):
        self.light.value(0)
        time.sleep_ms(10)
        self.light.value(1)
        time.sleep_ms(100)
        self.light.value(0)

class ButtonPressWatcher(object):
    def __init__(self):
        self.button = Pin(13, Pin.IN, Pin.PULL_UP)
        self.press_count = 0
        self.needs_exit = False
        self.was_pressed = False

        self.self_timer = Timer(-1)
        self.self_timer.init(period=20, mode=Timer.PERIODIC, callback=self.timer_callback)

    def timer_callback(self, t):
        value = self.button.value()

        if value == 0:
            self.down_times += 1
        if value == 1:
            self.down_times = 0

        if self.down_times == 2:
            self.press_count += 1
            self.was_pressed = True

    def loop(self, callback=None):
        if self.needs_exit:
            self.exit()

        if self.was_pressed:
            self.was_pressed = False
            if callback:
                callback()

    def exit(self):
        print('press_count', self.press_count)
        print('MHz', freq())
        sys.exit()

class LightToggler(object):
    def __init__(self):
        self.sending_request = False
        pass

    def toggle(self):
        """
        POST request to turn off light
        """
        print('toggle() 1')

        sta = network.WLAN(network.STA_IF)
        print(sta.ifconfig())

        self.sending_request = True
        try:
            r = urequests.request('POST', post_url, post_body)
            _ = r.text
            print('got response', r.text)
        finally:
            self.sending_request = False

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
    wifi_connection = WifiConnection()
    button_press_watcher = ButtonPressWatcher()
    test_light = TestLight()
    light_toggler = LightToggler()

    test_light.blink_on()

    def on_click():
        test_light.blink_on()
        light_toggler.toggle()

    count = 0
    while True:
        button_press_watcher.loop(on_click)
        time.sleep_ms(100)
    while False: # remove to exit after 50 loops
        count += 1
        if count > 50:
            test_light.blink_on()
            button_press_watcher.exit()
            #sys.exit()

