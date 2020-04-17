import logging
import time
from threading import Thread

import cflib
from cflib.crazyflie import Crazyflie

import matlab.engine

logging.basicConfig(level=logging.ERROR)

class CFConnect:

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie(rw_cache='./cache')

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.open_link(link_uri)

        print('Connecting to %s' % link_uri)

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""

        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!

        print('Connected to %s' % link_uri) 
        
        #Thread(target=self._ramp_motors).start()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)

    def _ramp_motors(self):
        # thrust_mult = 1
        # thrust_step = 500
        # thrust = 20000
        # pitch = 0
        # roll = 0
        # yawrate = 0
        cmd_rate = 0.05
        ramp_time = 2
        stay_time = 1
        thrust = 0
        tcounter = 0.0

        # Unlock startup thrust protection
        self._cf.commander.send_setpoint(0, 0, 0, 0)

        while thrust < 65535:
            self._cf.commander.send_setpoint(0, 0, 0, thrust)
            time.sleep(cmd_rate)
            thrust += 65535 / ramp_time * cmd_rate
            if thrust >= 65535:
                thrust = 65535
        self._cf.commander.send_setpoint(0, 0, 0, thrust)

        while tcounter < stay_time:
            self._cf.commander.send_setpoint(0, 0, 0, thrust)
            tcounter += cmd_rate
            time.sleep(cmd_rate)

        while thrust > 0:
            self._cf.commander.send_setpoint(0, 0, 0, thrust)
            time.sleep(cmd_rate)
            thrust -= 65535 / ramp_time * cmd_rate
            if thrust <= 0:
                thrust = 0
        self._cf.commander.send_setpoint(0, 0, 0, thrust)
        time.sleep(0.1)

        self._cf.close_link()

class SimConnect:
    def __init__(self, modelName = 'simPlant'):
        self.modelName = modelName

    def setFeedback(self)


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Crazyflies and use the first one found
    print('Scanning interfaces for Crazyflies...')
    available = cflib.crtp.scan_interfaces()
    print('Crazyflies found:')
    for i in available:
        print(i[0])

    if len(available) > 0:
        le = CFConnect(available[0][0])
    else:
        print('No Crazyflies found, cannot run example')
