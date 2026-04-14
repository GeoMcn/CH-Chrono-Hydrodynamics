%% CH Framework: Galactic Wind & W-Well Distortion (Universal Case-Fix)
% Filename: CH_Galactic_Wind_Distortion.m
clear; clc; close all;

% --- CH CONSTANTS ---
h_planck = 6.626; hbar = h_planck / (2*pi); m_vacuum = 6.630;
xmin = -20; xmax = 20; Nx = 128; ymin = -20; ymax = 20; Ny = 128;
Geometry2D = Geometry2D_Var2d(xmin, xmax, ymin, ymax, Nx, Ny);

% --- METHOD & PHYSICS ---
Method = Method_Var2d('Ground', 1, 'BESP'); 
Method.Deltat = 0.05; 
Method.Max_iter = 1000;
Physics2D = Physics2D_Var2d(Method);
Physics2D.g = 20000; 

% --- THE GALACTIC WIND INITIALIZATION ---
v_wind = 0.5; 
Phi_0 = {sqrt(50) * exp(1i * v_wind * Geometry2D.X)}; 

% --- THE PLANETARY MASS ---
Mass_Earth = 100; Sigma = 1.5;
Earth_Func = @(X,Y) Mass_Earth * exp(-(X.^2 + Y.^2)/(2*Sigma^2));
Physics2D = Potential_Var2d(Method, Physics2D, {Earth_Func});

% --- THE UNIVERSAL SATIATION FIX ---
Outputs = struct();
f = {'User_compute_global','User_compute_local','User_compute_evolution','User_compute_functional','User_compute_custom','User_compute_functionals','Save','Evo','Evo_outputs','Evo_functionals','Figure','Draw','Solution_name','Backup_solution','Save_solution','Iterations','Max_iter'};
for i=1:length(f); Outputs.(f{i})=0; end; 

% Dummy data to satisfy case-sensitive reporting engines
dummy = {zeros(1, 1001)};
Outputs.phi_abs_0 = dummy;
Outputs.x_rms = dummy;
Outputs.y_rms = dummy;
% Provide both case variants for all critical reporting fields
Outputs.energy = dummy;            Outputs.Energy = dummy;
Outputs.chemical_potential = dummy; Outputs.Chemical_potential = dummy;
Outputs.stopping_criterion = dummy; Outputs.Stopping_criterion = dummy;
Outputs.angular_momentum = dummy;   Outputs.Angular_momentum = dummy;
Outputs.energy_evolution = dummy;   Outputs.Energy_evolution = dummy;

Outputs.Iterations = 1; 
Outputs.Max_iter = 1000;

fprintf('Simulating W-Well in Galactic Wind (v=%.2f)...\n', v_wind);

% Execute
[Phi, ~] = GPELab2d(Phi_0, Method, Geometry2D, Physics2D, Outputs);

% --- POST-PROCESS: EXTRACT Q-POTENTIAL ---
Phi_F = Phi{1};
rho = abs(Phi_F).^2;
sqrt_rho = sqrt(rho);
dx = (xmax-xmin)/Nx;
[gx, gy] = gradient(sqrt_rho, dx);
[lxx, ~] = gradient(gx, dx);
[~, lyy] = gradient(gy, dx);
Q = -(hbar^2 / (2 * m_vacuum)) * ((lxx + lyy) ./ (sqrt_rho + 1e-2));

% --- VISUALIZATION ---
r = linspace(xmin, xmax, Nx);
Q_slice = Q(round(Ny/2), :);

figure('Color', 'w', 'Name', 'CH Forensic: Galactic Wind Distortion');
plot(r, Q_slice, 'b', 'LineWidth', 2); hold on; grid on;
title(['W-Well Distortion: Galactic Wind Velocity v = ', num2str(v_wind)]);

mid = round(Nx/2);
[minL, idxL] = min(Q_slice(1:mid));
[minR, idxR] = min(Q_slice(mid+1:end));
idxR = idxR + mid;

plot(r(idxL), minL, 'ro', 'MarkerFaceColor', 'r');
plot(r(idxR), minR, 'go', 'MarkerFaceColor', 'g');
legend('Potential Profile', 'Windward (Red)', 'Leeward (Green)');

fprintf('\n--- ASYMMETRY AUDIT ---\n');
fprintf('Windward Trough (Red): %.6f\n', minL);
fprintf('Leeward Trough (Green): %.6f\n', minR);
fprintf('Pressure Differential: %.6e\n', abs(minL - minR));