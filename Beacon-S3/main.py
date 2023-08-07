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
            
            self.brightness_mult = 10
            self.np = neopixel.NeoPixel(machine.Pin(42), 1)
            self._ble = ble
            self._ble.active(True)
            self._ble.irq(self._irq)
            ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
            self._payload = advertising_payload(name=self.name,
                                                services=[_UART_UUID])
            self._advertise()
            self._ble.config(gap_name=self.name)
            self._set_pixel((255, 255, 255))
            #self.connect_wifi()


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
                self._advertise()


        def _advertise(self, interval_us=500000):
            print("Starting advertising")
            self._ble.gap_advertise(interval_us, adv_data=self._payload)

        

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
            time.sleep_ms(1000)
# try:                
# except Exception as e:
#    print (e)


    demo()





except Exception as e:
    print(e)



