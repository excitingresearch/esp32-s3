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
        def __init__(self, ble, name="moody_001"):

            self.i2c = machine.SoftI2C(sda=machine.Pin(1, pull=machine.Pin.PULL_UP), scl=machine.Pin(2, pull=machine.Pin.PULL_UP), freq=100000)   
            self.irsensor = mlx90615.MLX90615(self.i2c)

            self.np = neopixel.NeoPixel(machine.Pin(42), 1)
            self._ble = ble
            self._ble.active(True)
            self._ble.irq(self._irq)
            ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
            self._connections = set()
            self._write_callback = self.on_write
            self._payload = advertising_payload(name="moody",
             services=[_UART_UUID])
            self._advertise()
            self._ble.config(gap_name=name)
            self._set_pixel((0,255,0))
            self.connect_wifi()

        
        def _set_pixel(self,c):
            self.np[0] = c
            self.np.write()    

        def _get_pixel(self):
            c = self.np[0]
            return c        
    
        def _irq(self, event, data):
            # Track connections so we can send notifications.
            if event == _IRQ_CENTRAL_CONNECT:
                self._set_pixel((0,0,255))
                conn_handle, _, _ = data
                print("New connection", conn_handle)
                self._connections.add(conn_handle)
            elif event == _IRQ_CENTRAL_DISCONNECT:
                conn_handle, _, _ = data
                print("Disconnected", conn_handle)
                self._connections.remove(conn_handle)
                # Start advertising again to allow a new connection.
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
            msg_type = int(v[:1],16)
            if msg_type == 1 :
                self._set_pixel((int(v[1:3],16),int(v[3:5],16), int(v[5:7],16)))
                print("RX", v)
            elif msg_type == 2:
                self._set_pixel((0,0,0))
                print("going to sleep for "+ str(int(v[1:],16))+ "microsecs")
                machine.deepsleep(int(v[1:],16))    
            #self._write_callback = callback


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
        
        def connect_wifi(self):
            ssid = 'Moody-net'
            pwd = 'ExcitingResearch'
            sta_if = network.WLAN(network.STA_IF)
            if not sta_if.isconnected():
                if self.check_wifi():
                    print('connecting to network...')
                    sta_if.active(True)
                    sta_if.connect(ssid, pwd)
                    while not sta_if.isconnected():
                        pass
                    print('network config:', sta_if.ifconfig())
                    webrepl.start()
                    c_col = self._get_pixel()
                    for _ in range(5):
                        self._set_pixel((255,20,147))
                        time.sleep_ms(100)
                        self._set_pixel((0,0,0))
                        time.sleep_ms(100)
                    self._set_pixel(c_col)    
                else:
                    print("Unable to connect to wifi, no Moody-net")    
            
    
    
    def demo():
        ble = bluetooth.BLE()
        p = BLESimplePeripheral(ble)
    
        #def on_rx(v):
        #    print("RX", v)
    
        #p.on_write(on_rx)
    
        t_val = 0

            
        while True:
            if p.is_connected():
                # Short burst of queued notifications.
                try:
                    t_val = p.irsensor.read_object_temp()
                except Exception as e:
                    print (e)
                data = str(t_val)
                print("TX", data)
                p.send(data)
            time.sleep_ms(1000)
    
    demo()    
    
    

    
    
except Exception as e:
    print(e)
    
 

