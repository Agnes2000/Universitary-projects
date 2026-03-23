function dp = f(t)
if t < 20
dp = [0.7; 0.3; -0.2];
elseif t < 30
dp = [0.3; -0.2; 0.4];
else
dp = [-0.1; 0.6; 0.4];
end
