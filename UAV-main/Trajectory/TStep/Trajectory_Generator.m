function [p_d, dp_d, ddp_d, psi_d] = trajectory_generator_step(t)
% Traiettoria desiderata a gradino (step)
% Cambio netto della posizione desiderata a t = 40 s

% Posizione iniziale (prima dello step)
p1 = [0; 0; 1];

% Posizione dopo lo step
p2 = [1; 1; 1.5];

% Cambia posizione a 40 secondi
if t < 40
p_d = p1;
dp_d = [0; 0; 0];
ddp_d = [0; 0; 0];
else
p_d = p2;
dp_d = [0; 0; 0];
ddp_d = [0; 0; 0];
end

% Orientamento desiderato (ad esempio fisso)
psi_d = 0;
