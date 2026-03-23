function [p_d, dp_d, ddp_d, psi_d] = trajectory_generator(data, t)
% Parametri esempio per traiettoria sinusoidale
p_d = [0.5*sin(0.1*t);
       0.5*cos(0.1*t);
       1 + 0.2*sin(0.05*t)];

dp_d = [0.05*cos(0.1*t);
       -0.05*sin(0.1*t);
        0.01*cos(0.05*t)];

ddp_d = [-0.005*sin(0.1*t);
         -0.005*cos(0.1*t);
         -0.0005*sin(0.05*t)];

psi_d = 0.1*t; % yaw cresce linearmente
