import matlab.engine
import matplotlib.pyplot as plt

import logging
import time
from threading import Thread
from cflib.crazyflie.log import LogConfig

import cflib
from cflib.crazyflie import Crazyflie

logging.basicConfig(level=logging.ERROR)

class SimulinkPlant:
    def __init__(self,modelName = 'simu_4qc_transform2018a'):
        
        self.modelName = modelName #The name of the Simulink Model (To be placed in the same directory as the Python Code) 
        #Logging the variables
        self.thrust = 0
        self.alpha = 0
        self.beta = 0
        
    def setControlAction(self,quat_x):
        #Helper Function to set value of control action
        self.eng.set_param('{}/py_quat_x'.format(self.modelName),'value',str(quat_x),nargout=0)
    
    def getHistory(self):
        #Helper Function to get Plant Output and Time History
        return self.eng.workspace['py_thrust'],self.eng.workspace['py_alpha'],self.eng.workspace['py_beta']
        
    def connectToMatlab(self):
        
        print("Starting matlab")
        self.eng = matlab.engine.start_matlab()
        
        print("Connected to Matlab")
        
        #Load the model
        self.eng.eval("model = '{}'".format(self.modelName),nargout=0)
        self.eng.eval("load_system(model)",nargout=0)
        
        #Initialize Control Action to 0
        self.setControlAction(0)
        print("Initialized Simulink Model")
        
        #Start Simulation and then Instantly pause
        self.eng.set_param(self.modelName,'SimulationCommand','start','SimulationCommand','pause',nargout=0)
        self.thrust,self.alpha,self.beta = self.getHistory()

        print('thrust = %s' % self.thrust)
    
    def connectController(self,controller):
        self.controller = controller
    
    def simulate(self):
        # Control Loop
        while(self.eng.get_param(self.modelName,'SimulationStatus') != ('stopped' or 'terminating')):
            
            #Pause the Simulation for each timestep
            self.eng.set_param(self.modelName,'SimulationCommand','continue',nargout=0)
            time.sleep(0.01)
            self.eng.set_param(self.modelName,'SimulationCommand','pause',nargout=0)
            self.thrust,self.alpha,self.beta = self.getHistory()

            self.controller.send_simu_cmd(self.thrust, self.alpha, self.beta)

            

            print("alpha = %s,      beta = %s" % (self.alpha, self.beta))

        self.controller.send_simu_cmd(0, 0, 0)
        
    def disconnect(self):
        self.eng.set_param(self.modelName,'SimulationCommand','stop',nargout=0)
        self.eng.quit()


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

        """
        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='sctrl', period_in_ms=100)
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

        """

        # Thread(target=self._step_motors).start()

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

    def send_simu_cmd(self, thrust, alpha, beta):
        self.thrust = thrust
        self.alpha = alpha
        self.beta = beta

        self._cf.commander.send_twod(0, 1, 0, 0, 0, alpha, beta, thrust)

    def disconnect(self):
        self._cf.close_link()


if __name__ == '__main__':

    plant = SimulinkPlant(modelName="simu_4qc_transform2018a")
    plant.connectToMatlab()

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

    plant.connectController(le)

    plant.simulate()

    plant.disconnect()

    le.disconnect()


