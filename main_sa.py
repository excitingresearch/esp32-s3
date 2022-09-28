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



cmap = [0x00,0x52,0x00,0x52,0x00,0x52,0x00,0x72,0x00,0x92,0x00,0x92,0x00,0xb2,0x00,0xd3,0x00,0xd3,0x00,0xf3,0x01,0x13,0x01,0x13,0x01,0x34,0x01,0x54,0x01,0x74,0x01,0x74,0x01,0x94,0x01,0xb5,0x01,0xd5,0x01,0xf5,0x02,0x15,0x02,0x36,0x02,0x56,0x02,0x56,0x02,0x77,0x02,0x97,0x02,0xb7,0x02,0xd7,0x02,0xf8,0x03,0x18,0x03,0x38,0x03,0x58,0x03,0x79,0x03,0x99,0x03,0xb9,0x03,0xda,0x03,0xfa,0x04,0x3b,0x04,0x7b,0x04,0xbc,0x04,0xfc,0x05,0x1d,0x05,0x5d,0x05,0x9d,0x05,0xbe,0x05,0xfe,0x06,0x1e,0x06,0x3f,0x06,0x7f,0x06,0x9f,0x06,0xbf,0x06,0xff,0x07,0x1f,0x07,0x1f,0x07,0x3f,0x07,0x5f,0x07,0x5f,0x07,0x5f,0x07,0x5f,0x07,0x5f,0x07,0x5f,0x07,0x5e,0x07,0x5e,0x07,0x5d,0x07,0x5d,0x07,0x5d,0x07,0x5c,0x07,0x5c,0x07,0x5b,0x07,0x5b,0x07,0x5a,0x07,0x59,0x07,0x39,0x07,0x38,0x07,0x38,0x07,0x17,0x06,0xf6,0x06,0xf6,0x06,0xd5,0x06,0xd4,0x06,0xb4,0x06,0xb3,0x06,0xb3,0x06,0x93,0x06,0x92,0x06,0x72,0x06,0x71,0x06,0x71,0x06,0x50,0x06,0x50,0x06,0x4f,0x06,0x2f,0x06,0x2f,0x06,0x2e,0x06,0x0e,0x06,0x0d,0x06,0x0d,0x05,0xec,0x05,0xec,0x05,0xec,0x05,0xcb,0x05,0xcb,0x05,0xca,0x05,0xca,0x05,0xaa,0x05,0xa9,0x05,0xa9,0x05,0xa9,0x05,0xa8,0x05,0xa8,0x05,0xa8,0x05,0xa8,0x05,0xa7,0x05,0xa7,0x05,0xa7,0x05,0xa7,0x05,0xa6,0x05,0xa6,0x0d,0xa6,0x0d,0xa6,0x0d,0xa5,0x15,0xc5,0x15,0xc5,0x1d,0xc5,0x1d,0xe5,0x25,0xe4,0x25,0xe4,0x26,0x04,0x2e,0x04,0x2e,0x04,0x36,0x24,0x36,0x24,0x3e,0x23,0x3e,0x43,0x46,0x43,0x4e,0x63,0x4e,0x63,0x56,0x83,0x56,0x83,0x5e,0xa2,0x5e,0xa2,0x66,0xc2,0x6e,0xc2,0x6e,0xe2,0x76,0xe2,0x77,0x02,0x7f,0x02,0x87,0x22,0x87,0x22,0x8f,0x41,0x8f,0x41,0x97,0x61,0x9f,0x61,0x9f,0x81,0xa7,0x81,0xa7,0x81,0xaf,0xa1,0xb7,0xa1,0xb7,0xc1,0xbf,0xc1,0xbf,0xc1,0xc7,0xc1,0xc7,0xe1,0xcf,0xe1,0xcf,0xe0,0xd7,0xe0,0xd7,0xe0,0xdf,0xe0,0xdf,0xe0,0xe7,0xe0,0xe7,0xe0,0xe7,0xe0,0xef,0xe0,0xef,0xe0,0xf7,0xe0,0xf7,0xe0,0xf7,0xe0,0xff,0xe0,0xff,0xe0,0xff,0xe0,0xff,0xe0,0xff,0xc0,0xff,0xc0,0xff,0xa0,0xff,0xa0,0xff,0x80,0xff,0x60,0xff,0x60,0xff,0x40,0xff,0x20,0xff,0x00,0xfe,0xe0,0xfe,0xe0,0xfe,0xc0,0xfe,0xa0,0xfe,0x80,0xfe,0x60,0xfe,0x40,0xfe,0x00,0xfd,0xe0,0xfd,0xc0,0xfd,0xa0,0xfd,0x80,0xfd,0x60,0xfd,0x20,0xfd,0x00,0xfc,0xe0,0xfc,0xa0,0xfc,0x80,0xfc,0x60,0xfc,0x40,0xfc,0x00,0xfb,0xe0,0xfb,0xc0,0xfb,0x80,0xfb,0x60,0xfb,0x40,0xfb,0x00,0xfa,0xe0,0xfa,0xc0,0xfa,0xa0,0xfa,0x60,0xfa,0x40,0xfa,0x20,0xfa,0x00,0xf9,0xe0,0xf9,0xc0,0xf9,0x80,0xf9,0x60,0xf9,0x40,0xf9,0x20,0xf9,0x00,0xf8,0xe0,0xf8,0xc0,0xf8,0xa0,0xf8,0xa0,0xf8,0x80,0xf8,0x60,0xf8,0x40,0xf8,0x20,0xf8,0x20,0xf8,0x00,0xf8,0x00,0xf8,0x00,0xf8,0x00,0xf8,0x00,0xf8,0x00,0xf8,0x00,0xf8,0x00,0xf8,0x00,0xf0,0x00,0xf0,0x00,0xf0,0x00,0xf0,0x00,0xe8,0x00,0xe8,0x00]







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
        def __init__(self, ble, name="moody_111"):

            self.i2c = machine.SoftI2C(sda=machine.Pin(1, pull=machine.Pin.PULL_UP), scl=machine.Pin(2, pull=machine.Pin.PULL_UP), freq=100000)   
            self.irsensor = mlx90615.MLX90615(self.i2c)

            self.richting = 0
            self.coldTemp = 0.0
            self.mediumTemp = 0.0
            self.hotTemp = 0.0
            self.initTemp = 0.0
            self.avgTemp = 0.0
            self.minTemp = 100.0
            self.maxTemp = 0.0
            self.envTemp = 0.0
            self.dTemp = 0.0
            self._Temp = 0.0
            self.iColor = 0
            self.avgiColor = 0
            self._i = 0
            self._r = 0
            self._g = 0
            self._b = 0


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

                    
        def calc_color(self, result):
            self._Temp = result
            if (self.initTemp == 0.0): 
                self.initTemp = result

            if result < 45 and result > 15:
                self.avgTemp += result
            self._override = result
            if (self.richting == 1 and result < self.initTemp):
                self._override = result - ((self.initTemp - result) * 4)
            if (self.richting == 0 and result > self.initTemp): 
                self._override = result + ((result - self.initTemp) * 4)
            if (result < self.minTemp):
                self.minTemp = result
            if (result > self.maxTemp):
                self.maxTemp = result
            self.dTemp = self.maxTemp - self.minTemp
            self.iColor = (self._override - self.minTemp) * (255 / self.dTemp)
            if (self.iColor > 255):
                self.iColor = 255
            if (self.iColor < 0):
                iColor = 0
            hibyte = cmap[int(self.iColor * 2)]
            lobyte = cmap[int(self.iColor * 2 + 1)]
            colorrgb = (hibyte << 8) + lobyte 
            r = (0b1111100000000000 & colorrgb) >> 11
            g = (0b0000011111100000 & colorrgb) >> 5
            b = (0b0000000000011111 & colorrgb)

            self._r = (((self._r * self._r) + (r * r)) / 2)**(1/2)
            self._g = (((self._g * self._g) + (g * g)) / 2)**(1/2)
            self._b = (((self._b * self._b) + (b * b)) / 2)**(1/2)

            self._i += 1

            self.avgiColor += self.iColor
            self._ravgiColor = self.avgiColor / self._i
            self._ravg = self.avgTemp / self._i
            self._iravg = self._ravg
            self._cravg = (self._ravg - self._iravg) * 100

            self._set_pixel((r * 8, g*4, b*8))
                
            
    
    
    def demo():
        ble = bluetooth.BLE()
        p = BLESimplePeripheral(ble)
        

        period = 30000
    
        #def on_rx(v):
        #    print("RX", v)
    
        #p.on_write(on_rx)
    
        t_val = 0

        btime = time.time()    
        while True:
            if p.is_connected():
                currentMillis = time.time()  # get the current "time" (actually the number of milliseconds since the program started)
                if (currentMillis - btime >= period):  #test whether the period has elapsed
                    minTemp = 100;
                    maxTemp = 0;
                    btime = currentMillis #   //IMPORTANT to save the start time of the current LED state.
                    print("min max reset")
  
                # Short burst of queued notifications.
                #try:
                t_val = p.irsensor.read_object_temp()
                p.calc_color(t_val)
                #except Exception as e:
                #    print (e)
                data = str(t_val)
                print("TX", data)
                p.send(data)
            time.sleep_ms(1000)
    
    demo()    
    
    

    
    
except Exception as e:
    print(e)
    
 

