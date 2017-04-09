from machine import freq, Pin, Timer
import ds18x20, network, onewire, socket, sys, time, urequests


time_to_send_temp = False
toggle_light_needed = False
sending_request = False

post_url = 'http://192.168.5.123:8123/api/services/switch/toggle'
post_body = '{"entity_id": "light.leviton_vrmx11lz_multilevel_scene_switch_level_40"}'
temp_url = 'http://192.168.5.123:8123/api/states/sensor.office_temp'

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

class ButtonPressWatcherB(object):
    def __init__(self):
        self.button = Pin(13, Pin.IN, Pin.PULL_UP)
        self.start_down_tick = 0
        self.end_down_tick = 0
        self.last_value = 0
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
        #self.button.irq(None)
        print('exit()')
        #print('timer_count', self.timer_count)
        print('press_count', self.press_count)
        print('MHz', freq())
        sys.exit()

class ButtonPressWatcher(object):
    def __init__(self):
        self.button = Pin(13, Pin.IN, Pin.PULL_UP)
        self.start_down_tick = 0
        self.end_down_tick = 0
        self.last_value = 0
        self.press_count = 0
        self.needs_exit = False
        self.was_pressed = False

        self.button_callback = self.button.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.button_change)

    def timer_callback(self, t):
        self.timer_count += 1
        if self.timer_count > 100:
            pass

    def button_change(self, event):
        value = self.button.value()
        print('a change', value)
        if value == 0:
            self.start_down_tick = time.ticks_ms()

        if value == 1 and self.last_value == 0:
            self.end_down_tick = time.ticks_ms()
            delta = time.ticks_diff(self.end_down_tick, self.start_down_tick)
            print('delta', delta)
            if self.start_down_tick < self.end_down_tick and delta > 20:
                self.was_pressed = True
                print('real press')
                self.press_count +=1

            # reset
            self.start_down_tick = 0


        self.last_value = value

    def loop(self, callback=None):
        if self.needs_exit:
            self.exit()

        if self.was_pressed:
            self.was_pressed = False
            if callback:
                callback()

    def exit(self):
        #self.button.irq(None)
        print('exit()')
        #print('timer_count', self.timer_count)
        print('press_count', self.press_count)
        print('MHz', freq())
        sys.exit()

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

count_butts = 0

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

    button_press_watcher = ButtonPressWatcherB()
    test_light = TestLight()

    test_light.blink_on()

    count = 0
    while True:
        button_press_watcher.loop(test_light.blink_on)
        #print('im sleepy')
        # button_press_watcher.fire()

        count += 1
        if count > 50:
            test_light.blink_on()
            button_press_watcher.exit()
            #sys.exit()

        time.sleep_ms(100)

loop_forever()
