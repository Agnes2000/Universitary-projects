function dp = disturbance_generator(t)
% Disturbo randomico smussato con rumore gaussiano filtrato

persistent prev_dp prev_ddp prev_t

if isempty(prev_dp)
    prev_dp = zeros(3,1);
    prev_ddp = zeros(3,1);
    prev_t = 0;
end

dt = t - prev_t;
if dt <= 0
    dt = 0.01; % timestep di sicurezza
end

% Parametri rumore
noise_std = 0.05;  % deviazione standard del rumore del disturbo

% Genero una variazione casuale accelerativa
random_ddisturb = noise_std * randn(3,1);

% Filtro esponenziale (valori tra 0.8 e 1.0 = lenti, tra 0.2 e 0.5 = rapidi)
ddp = 0.9 * prev_ddp + 0.1 * random_ddisturb;

% Integra per ottenere dp
dp = prev_dp + ddp * dt;

% Aggiorna stati
prev_ddp = ddp;
prev_dp = dp;
prev_t = t;
end
