from machine import Pin
import network, socket, time, urequests

button = Pin(12, Pin.IN, Pin.PULL_UP)
test_light = Pin(15, Pin.OUT)

toggle_light_needed = False
sending_request = False

post_url = 'http://192.168.5.123:8123/api/services/switch/toggle'
post_body = '{"entity_id": "switch.office_lamp_switch_2_0"}'

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

def toggle_light():
    global toggle_light_needed
    toggle_light_needed = False

    addr = socket.getaddrinfo('192.168.5.123', 8123)[0][-1]
    s = socket.socket()
    s.connect(addr)

    post = 'POST /api/services/switch/toggle HTTP/1.1'
    host = 'Host: 192.168.5.123:8123'
    agent = 'User-Agent: button/1.0'
    content_length = 'Content-Length: 46'
    body = '{"entity_id": "switch.office_lamp_switch_2_0"}'
    accept = 'Accept: */*'
    type_ = 'Content-Type: application/x-www-form-urlencoded'

    payload = '%s\r\n%s\r\n%s\r\n%s\r\n%s\r\n%s\r\n\r\n%s\r\n\r\n' % (post, host, agent, accept, content_length, type_, body)

    #print('sending...')
    #print(payload)

    s.send(bytes(payload, 'utf8'))

    #print('sent...')

def button_callback(p):
    global toggle_light_needed
    toggle_light_needed = True

button.irq(trigger=Pin.IRQ_RISING, handler=button_callback)

# keeping line here because connection fails if it's removed
sta = network.WLAN(network.STA_IF)

def loop_forever():
    global x, toggle_light_needed, test_light
    while True:
        # print(sta.ifconfig())
        # print('x', x)
        time.sleep_ms(200)
        test_light.value(not test_light.value())
        if toggle_light_needed:
            toggle_light_needed = False
            toggle_light_urequests()

