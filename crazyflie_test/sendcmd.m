function y = fcn(ramp,a)

coder.extrinsic('py.list') 

a.commander.send_setpoint(0,0,0,ramp);

y = ramp;

end
