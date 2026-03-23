function [p_d, dp_d, ddp_d, psi_d] = trajectory_generator(t)
% Traiettoria randomica smussata generata tramite rumore filtrato

persistent prev_p prev_dp prev_ddp prev_psi prev_t

if isempty(prev_p)
    prev_p = zeros(3,1);
    prev_dp = zeros(3,1);
    prev_ddp = zeros(3,1);
    prev_psi = 0;
    prev_t = 0;
end

dt = t - prev_t;
if dt <= 0
    dt = 0.01; % default timestep per sicurezza
end

% Parametri rumore
noise_std_pos = 0.02;  % deviazione standard posizione (modificabile)
noise_std_psi = 0.01;  % deviazione standard orientamento

% Genero variazione accelerazione random gaussiana
random_accel = noise_std_pos * randn(3,1);

% Aggiorno accelerazione
ddp_d = prev_ddp * 0.8 + random_accel * 0.2; % filtro esponenziale per smussare

% Aggiorno velocità e posizione (integrazione numerica semplice)
dp_d = prev_dp + ddp_d * dt;
p_d = prev_p + dp_d * dt;

% Orientamento yaw: random walk smussato
dpsi = noise_std_psi * randn;
psi_d = prev_psi + dpsi;

% Aggiorno valori persistenti
prev_p = p_d;
prev_dp = dp_d;
prev_ddp = ddp_d;
prev_psi = psi_d;
prev_t = t;

end
