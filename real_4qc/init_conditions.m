% ====== constants ======
g = 9.81;
m_main = 0.012; % mass of main frame
m_qc = 0.03; % mass of qc
m = (m_qc+0.006)*4 + m_main; %total mass 0.036*4 + 0.012;
IBxy = 0.0024; % inertia in x and y direction 2*0.036*0.18^2 + 3e-5
IBz = 0.0048; % inertia in z direction 4*0.036*0.18^2 + 6e-5
IB = diag([IBxy, IBxy, IBz]);
Lh = 0.001; % vertical offset in negative z 
Lw = 0.18; % from system center to qc center

fd0 = [0;0;m*g/4;0;0;m*g/4;0;0;m*g/4;0;0;m*g/4];

% ====== low level PID gains ======
% pgain = 1e-3;
% igain = 0;
% dgain = 2e-4;

% pgaina = 8e-3;
% igaina = 0;
% dgaina = 5e-4;
% 
% pgainb = 8e-3;
% igainb = 0;
% dgainb = 5e-4;

pgaina = 1.5e-4;
igaina = 0e-5;
dgaina = 4e-5;

pgainb = pgaina;
igainb = igaina;
dgainb = dgaina;

% % ====== trajectory ======
% StepSize = 0.01;
% t1 = 3;
% t2 = 10;
% Tpad = 20;
% 
% t1array = 0:StepSize:t1;
% t2array = StepSize:StepSize:t2;
% num1 = length(t1array);
% num2 = length(t2array);
% 
% numpad = Tpad/StepSize;
% 
% % % ---------- angle ------------
% % % position trajectory
% % np1 = ones(num1,1) * [0,0,0];
% % 
% % x2 = 0*sin( 2*pi/5 * t2array);
% % y2 = 0*(cos( 2*pi/5 * t2array)-1);
% % np2 = [x2.', y2.', zeros(num2,1)];
% % %np2 = zeros(num2,3);
% % 
% % np = [np1; np2; ones(numpad,1)*np2(end,:)];
% % 
% % % attitude trajectory
% % th = deg2rad(linspace(0, 80, num2));
% % 
% % 
% % phi = zeros(num1+num2+numpad, 1);
% % the = [zeros(1,num1), th, th(end) * ones(1, numpad)].';
% % psi = zeros(num1+num2+numpad, 1);
% 
% % ---------- angle 2 ------------
% % position trajectory
% np1 = ones(num1,1) * [0,0,0];
% 
% x2 = 0*sin( 2*pi/5 * t2array);
% y2 = 0*(cos( 2*pi/5 * t2array)-1);
% np2 = [x2.', y2.', zeros(num2,1)];
% %np2 = zeros(num2,3);
% 
% np = [np1; np2; ones(numpad,1)*np2(end,:)];
% 
% % attitude trajectory
% th1 = deg2rad(linspace(0, 20, num2/2));
% th2 = deg2rad(linspace(20, 0, num2/2));
% 
% 
% phi = zeros(num1+num2+numpad, 1);
% the = [zeros(1,num1), th1, th2, th2(end) * ones(1, numpad)].';
% psi = zeros(num1+num2+numpad, 1);
% 
% % % ----------- position --------------
% % % position trajectory
% % np1 = ones(num1,1) * [0,0,0];
% % 
% % x2 = 0.5*sin( 2*pi/2 * t2array);
% % y2 = 0.5*(cos( 2*pi/2 * t2array)-1);
% % np2 = [x2.', y2.', zeros(num2,1)];
% % %np2 = zeros(num2,3);
% % 
% % np = [np1; np2; ones(numpad,1)*np2(end,:)];
% % 
% % % attitude trajectory
% % th = deg2rad(linspace(0, 0, num2));
% % 
% % 
% % phi = zeros(num1+num2+numpad, 1);
% % the = [zeros(1,num1), th, th(end) * ones(1, numpad)].';
% % psi = zeros(num1+num2+numpad, 1);

% ====== trajectory for both angle and position ======
StepSize = 0.01;
t1 = 2;
t2 = 6;
t3 = 10;
t4 = 10;
t5 = 6;
Tpad = 20;

t1array = 0:StepSize:t1;
t2array = StepSize:StepSize:t2;
t3array = StepSize:StepSize:t3;
t4array = StepSize:StepSize:t4;
t5array = StepSize:StepSize:t5;
num1 = length(t1array);
num2 = length(t2array);
num3 = length(t3array);
num4 = length(t4array);
num5 = length(t5array);

numpad = Tpad/StepSize;


% ----------- both angle and position --------------
% position trajectory
np1 = ones(num1,1) * [0,0,0];

x2 = 0.5*sin( 4*pi/t2 * t2array);
y2 = 0.5*(cos( 4*pi/t2 * t2array)-1);
np2 = [x2.', y2.', zeros(num2,1)];

np3 = ones(num3,1) * [0,0,0];

x4 = 0.5*sin( 2*pi/t4 * t4array);
y4 = 0.5*(cos( 2*pi/t4 * t4array)-1);
np4 = [x4.', y4.', zeros(num4,1)];

np5 = ones(num5,1) * [0,0,0];

np = [np1; np2; np3; np4; np5; ones(numpad,1)*np5(end,:)];

% attitude trajectory
th = deg2rad(linspace(0, 30, num3));


phi = zeros(num1+num2+num3+num4+num5+numpad, 1);
the = [zeros(1,num1+num2), th, th(end) * ones(1, num4+num5+numpad)].';
psi = zeros(num1+num2+num3+num4+num5+numpad, 1);


