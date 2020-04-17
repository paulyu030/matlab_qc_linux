
% steps to connect a crazyflie and make 'drone' python object
py.cflib.crtp.init_drivers;

available = py.cflib.crtp.scan_interfaces;
drone = py.cfconnection.CFSimulink(available{1}{1})

a = py.getattr(drone,'_cf');

% for i=1:100
%     ramp = ramp + 100;
%     a.commander.send_setpoint(0,0,0,ramp);
%     pause(0.03);
% end
% 
% for i=1:100
%     ramp = ramp - 100;
%     a.commander.send_setpoint(0,0,0,ramp);
%     pause(0.03);
% end
% 
% a.close_link();





