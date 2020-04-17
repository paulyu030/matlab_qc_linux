
import logging
import time
from threading import Thread
from cflib.crazyflie.log import LogConfig

import cflib
from cflib.crazyflie import Crazyflie

logging.basicConfig(level=logging.ERROR)


class ThrustRamp:

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

        # The definition of the logconfig can be made before connecting
        
        self._lg_stab = LogConfig(name='sctrl', period_in_ms=10)
        # self._lg_stab.add_variable('sctrl.t_be')
        # self._lg_stab.add_variable('sctrl.t_ae')
        # self._lg_stab.add_variable('sctrl.t_bin')

        
        # self._lg_stab.add_variable('sctrl.t_m1')
        # self._lg_stab.add_variable('sctrl.t_m2')
        # self._lg_stab.add_variable('sctrl.t_m3')
        # self._lg_stab.add_variable('sctrl.t_m4')
        

        self._lg_stab.add_variable('sctrl.error_beta')
        self._lg_stab.add_variable('sctrl.u_beta')
        # self._lg_stab.add_variable('sctrl.error_alpha')
        # self._lg_stab.add_variable('sctrl.u_alpha')
        # self._lg_stab.add_variable('sctrl.t_pbout')
        # self._lg_stab.add_variable('sctrl.t_ibout')
        # self._lg_stab.add_variable('sctrl.t_dbout')
        
        """
        self._lg_stab = LogConfig(name='motor', period_in_ms=40)
        self._lg_stab.add_variable('motor.m1')
        self._lg_stab.add_variable('motor.m2')
        self._lg_stab.add_variable('motor.m3')
        self._lg_stab.add_variable('motor.m4')
        """


        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_stab)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

        Thread(target=self._step_motors).start()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        print('[%d][%s]: %s' % (timestamp, logconf.name, data))

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
        ramp_time = 3
        stay_time = 1
        thrust = 0
        beta = 0
        tcounter = 0.0
        thrust_max = 20000
        beta_max = 3.14/6
        

        # Unlock startup thrust protection
        self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, 0, 0)

        while thrust < thrust_max:
            self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, beta, thrust)
            time.sleep(cmd_rate)
            thrust += thrust_max / ramp_time * cmd_rate
            beta += beta_max / ramp_time * cmd_rate
            if thrust >= thrust_max:
                thrust = thrust_max
        self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, beta, thrust)

        print('thrust is %s' % thrust)

        while tcounter < stay_time:
            self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, beta, thrust)
            tcounter += cmd_rate
            time.sleep(cmd_rate)

        while thrust > 0:
            self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, beta, thrust)
            time.sleep(cmd_rate)
            thrust -= thrust_max / ramp_time * cmd_rate
            beta -= beta_max / ramp_time * cmd_rate
            if thrust <= 0:
                thrust = 0
        self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, 0, thrust)
        time.sleep(0.1)

        self._cf.close_link()

    def _step_motors(self):
        cmd_rate = 0.01
        thrust = 20000
        alpha = 0
        beta = 3.14/4
        t = 0

        self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, 0, thrust)

        while t < 10:
            self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, 0, thrust)
            t += cmd_rate
            time.sleep(cmd_rate)

        """
        while t < 7:
            self._cf.commander.send_twod(0, 1, 0, 0, 0, alpha, beta, thrust)
            t += cmd_rate
            time.sleep(cmd_rate)
        """

        self._cf.commander.send_twod(0, 1, 0, 0, 0, alpha, beta, 0)
        time.sleep(0.1)

        self._cf.close_link()

    def _idle_motors(self):
        cmd_rate = 0.05
        t = 0

        while t < 30:
            self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, 0, 0)
            t += cmd_rate
            time.sleep(cmd_rate)

        self._cf.close_link()

    def _motor_order_test(self):
        cmd_rate = 0.05
        t = 0
        thrust = 100
        alpha = 1
        beta = 3.14/2

        self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, 0, 0)

        while t < 5:
            self._cf.commander.send_twod(0, 1, 0, 0, 0, alpha, beta, thrust)
            t += cmd_rate
            time.sleep(cmd_rate)

        self._cf.commander.send_twod(0, 1, 0, 0, 0, 0, 0, 0)
        time.sleep(0.1)

        self._cf.close_link()


        # while thrust >= 20000:
        #     self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
        #     time.sleep(0.1)
        #     if thrust >= 25000:
        #         thrust_mult = -1
        #     thrust += thrust_step * thrust_mult
        # self._cf.commander.send_setpoint(0, 0, 0, 0)
        # # Make sure that the last packet leaves before the link is closed
        # # since the message queue is not flushed before closing
        # time.sleep(0.1)
        # self._cf.close_link()


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
        le = ThrustRamp(available[0][0])
    else:
        print('No Crazyflies found, cannot run example')
