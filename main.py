import machine, neopixel
from machine import Pin, Timer
import time
import network

import ubluetooth
import bluetooth

import random
import struct
import webrepl

from ble_advertising import advertising_payload

from micropython import const

import mlx90615



try:

    _IRQ_CENTRAL_CONNECT = const(1)
    _IRQ_CENTRAL_DISCONNECT = const(2)
    _IRQ_GATTS_WRITE = const(3)

    _FLAG_READ = const(0x0002)
    _FLAG_WRITE_NO_RESPONSE = const(0x0004)
    _FLAG_WRITE = const(0x0008)
    _FLAG_NOTIFY = const(0x0010)

    _UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    _UART_TX = (
        bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
        _FLAG_READ | _FLAG_NOTIFY,
    )
    _UART_RX = (
        bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
        _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
    )
    _UART_SERVICE = (
        _UART_UUID,
        (_UART_TX, _UART_RX),
    )


    class BLESimplePeripheral:
        def __init__(self, ble, name="m003"):
            self.name = name
            self.i2c = machine.SoftI2C(sda=machine.Pin(1, pull=machine.Pin.PULL_UP),
                                       scl=machine.Pin(2, pull=machine.Pin.PULL_UP), freq=100000)
            self.irsensor = mlx90615.MLX90615(self.i2c)

            self.temps = []

            self.update_interval = 1000
            self.brightness_mult = 100
            self._sa = False
            self.np = neopixel.NeoPixel(machine.Pin(42), 1)
            self._ble = ble
            self._ble.active(True)
            self._ble.irq(self._irq)
            ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
            self._connections = set()
            self._write_callback = self.on_write
            self._payload = advertising_payload(name=self.name,
                                                services=[_UART_UUID])
            self._advertise()
            self._ble.config(gap_name=self.name)
            self._set_pixel((0, 255, 0))
            self.connect_wifi()


        def _set_pixel(self, c):
            c = [int(e * self.brightness_mult/100) for e in c]
            #print(c)
            self.np[0] = c
            self.np.write()

        def _get_pixel(self):
            c = self.np[0]
            return c

        def _irq(self, event, data):
            # Track connections so we can send notifications.
            if event == _IRQ_CENTRAL_CONNECT:
                self._set_pixel((0, 0, 255))
                conn_handle, _, _ = data
                print("New connection", conn_handle)
                self._connections.add(conn_handle)
                self._advertise()
            elif event == _IRQ_CENTRAL_DISCONNECT:
                conn_handle, _, _ = data
                print("Disconnected", conn_handle)
                self._connections.remove(conn_handle)
                # Start advertising again to allow a new connection.
                self._set_pixel((0, 255, 0))
                self._advertise()
            elif event == _IRQ_GATTS_WRITE:
                conn_handle, value_handle = data
                value = self._ble.gatts_read(value_handle)
                if value_handle == self._handle_rx and self._write_callback:
                    self._write_callback(value)

        def send(self, data):
            for conn_handle in self._connections:
                self._ble.gatts_notify(conn_handle, self._handle_tx, data)

        def is_connected(self):
            return len(self._connections) > 0

        def _advertise(self, interval_us=500000):
            print("Starting advertising")
            self._ble.gap_advertise(interval_us, adv_data=self._payload)

        def on_write(self, v):
            msg_type = int(v[:1], 16)
            if msg_type == 1:
                self._set_pixel((int(v[1:3], 16), int(v[3:5], 16), int(v[5:7], 16)))
                print("RX", v)
            elif msg_type == 2:
                up_i = int(v[1:], 16)
                up_i = max(1, up_i)
                print("Update interval set to: ", up_i)
                self.update_interval = up_i
            elif msg_type == 3:
                bright = int(v[1:], 16) 
                bright = max(1, bright)
                bright = min(100, bright)
                print("Brightness set to: ", bright)
                self.brightness_mult = bright
            elif msg_type == 4:
                self._set_pixel((0, 0, 0))
                print("going to sleep for " + str(int(v[1:], 16)) + "microsecs")
                machine.deepsleep(int(v[1:], 16))
                # self._write_callback = callback
            elif msg_type == 5:
                self._sa = not self._sa
                print("Stand alone mode active: " + str(self._sa))
            else: 
                print("Unknown message: ", str(v))    

        def check_wifi(self):
            sta_if = network.WLAN(network.STA_IF)
            sta_if.active(True)
            nets = sta_if.scan()
            moody_net_av = False
            for e in nets:
                if len(e[0]) > 0 and e[0].decode('utf-8') == 'Moody-net':
                    moody_net_av = True
            if moody_net_av:
                print("Moody-net available")
            else:
                print("Moody-net not available")
            return moody_net_av

        def blink(self, c):
            self._set_pixel(c)
            time.sleep_ms(100)
            self._set_pixel((0, 0, 0))
            time.sleep_ms(100)

        def connect_wifi(self):
            ssid = 'Moody-net'
            pwd = 'ExcitingResearch'
            sta_if = network.WLAN(network.STA_IF)
            if not sta_if.isconnected():
                if self.check_wifi():
                    print('connecting to network...')
                    sta_if.active(True)
                    sta_if.connect(ssid, pwd)
                    time.sleep_ms(10000)
                    if sta_if.isconnected():
                        print('network config:', sta_if.ifconfig())
                        webrepl.start()
                        c_col = self._get_pixel()
                        wifi_c_pink = (255, 20, 147)
                        for _ in range(5):
                            self.blink(wifi_c_pink)
                        self._set_pixel(c_col)
                    else:
                        c_col = self._get_pixel()
                        wifi_c_f = (255, 0, 0)
                        for _ in range(5):
                            self.blink(wifi_c_f)
                        self._set_pixel(c_col)   
                        print("Unable to connect to wifi, error with Moody-net")

                else:
                    print("Unable to connect to wifi, no Moody-net")

        def calc_color(self, result):
            result = result/100
            self.temps.append(result)
            if len(self.temps) > 5:
                
                if len(self.temps) > 100:
                    self.temps = self.temps[1:]
                avgTemp = sum(self.temps) / len(self.temps)
                max_temp = max(self.temps)
                min_temp = min(self.temps)
                delta = result - avgTemp
                if abs(delta) < 0.02:
                    c = self._get_pixel()
                ## same
                #print("delta: ", delta, end=" ")
                elif delta < 0:
                    ## down
                    spr = avgTemp - min_temp
                    dev = -1*delta / spr
                    #print("downspread: ", spr, end=" ")
                    #print("downdev: ", dev)
                    cb = 255 * dev
                    cg = 255 * (1 - dev)
                    cb = max(0, cb)
                    cg = max(0, cg)
                    c = (0, int(cg), int(cb))
                elif delta > 0:
                    ## up
                    spr = max_temp - avgTemp
                    dev = delta / spr
                    #print("upspread: ", spr, end=" ")
                    #print("updev: ", dev)
                    cr = 255 *  dev
                    cg = 255 * (1- dev)
                    cr = max(0, cr)
                    cg = max(0, cg)
                    #print("uprgb: ", cr, " ", cg, " ", 0)
                    c = (int(cr), int(cg), 0)
                self._set_pixel(c)
                return c


    def demo():
        ble = bluetooth.BLE()
            
        try:
            f = open("name.txt")
            n = f.readline().strip()
            p = BLESimplePeripheral(ble,n)
        except Exception as e:
            p = BLESimplePeripheral(ble)
            print (e)

        t_val = 0
        
        while True:
            if p._sa:
                try:                
                    t_val = p.irsensor.read_object_temp()
                    p.calc_color(t_val)
                    time.sleep_ms(p.update_interval)
                except Exception as e:
                    print (e)

            else:
                if p.is_connected():
                    try:                
                        t_val = p.irsensor.read_object_temp()
                        col = p.calc_color(t_val)                        
                        data = str(t_val)
                        print("TX", data)
                        p.send(data +"|" +str(col))
                    except Exception as e:
                        print (e)

                time.sleep_ms(p.update_interval)
# try:                
# except Exception as e:
#    print (e)


    demo()





except Exception as e:
    print(e)



