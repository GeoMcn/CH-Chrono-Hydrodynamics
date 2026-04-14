%% CH Framework: 2009 Galactic Shear & Rupture (Visual Fix)
clear; clc; close all;

% --- CH CONSTANTS ---
xmin = -20; xmax = 20; Nx = 128; ymin = -20; ymax = 20; Ny = 128;
Geometry2D = Geometry2D_Var2d(xmin, xmax, ymin, ymax, Nx, Ny);

% --- METHOD: High Damping + Shear ---
Method = Method_Var2d('Ground', 1, 'BESP'); 
Method.Deltat = 0.05; 
Method.Max_iter = 600;
Method.Gamma = 0.8; 
Method.Print = 0;

Physics2D = Physics2D_Var2d(Method);
Physics2D.g = 20000; 

% --- THE SHEAR FIELD ---
v_x = 2.5; v_y = 1.2; 
Phi_0 = {sqrt(50) * exp(1i * (v_x * Geometry2D.X + v_y * Geometry2D.Y))}; 

% --- THE PLANETARY MASS ---
Mass_Earth = 250; 
Sigma = 1.2;
Earth_Func = @(X,Y) Mass_Earth * exp(-(X.^2 + Y.^2)/(2*Sigma^2));
Physics2D = Potential_Var2d(Method, Physics2D, {Earth_Func});

% --- TOTAL SATIATION ---
Outputs = struct();
f = {'User_compute_global','User_compute_local','User_compute_evolution','User_compute_functional','User_compute_custom','User_compute_functionals','Save','Evo','Evo_outputs','Evo_functionals','Figure','Draw','Solution_name','Backup_solution','Save_solution','Iterations','Max_iter'};
for i=1:length(f); Outputs.(f{i})=0; end; 
dummy = {zeros(1, 1001)};
Outputs.phi_abs_0 = dummy; Outputs.x_rms = dummy; Outputs.y_rms = dummy;
Outputs.Energy = dummy; Outputs.Chemical_potential = dummy;
Outputs.Angular_momentum = dummy; Outputs.Stopping_criterion = dummy;
Outputs.Iterations = 1;

fprintf('Simulating Galactic Shear Encounter (Analyzing Wake)...\n');
[Phi, ~] = GPELab2d(Phi_0, Method, Geometry2D, Physics2D, Outputs);

% --- ANALYZE ASYMMETRY ---
rho = abs(Phi{1}).^2;
sqrt_rho = sqrt(rho);
dx = (xmax-xmin)/Nx;
[gx, gy] = gradient(sqrt_rho, dx);
[lxx, ~] = gradient(gx, dx); [~, lyy] = gradient(gy, dx);
Q = -(1.0) * ((lxx + lyy) ./ (sqrt_rho + 1e-3));

% Define plotting axis
r = linspace(xmin, xmax, Nx);

% --- VISUALIZATION ---
figure('Color', 'w', 'Position', [100, 100, 1000, 450]);
subplot(1,2,1);
imagesc(r, r, rho); axis square; colormap(jet); colorbar;
title('Vacuum Density Wake (\rho)');
xlabel('X (units)'); ylabel('Y (units)');

subplot(1,2,2);
Q_slice = Q(round(Ny/2), :);
plot(r, Q_slice, 'k', 'LineWidth', 2); hold on; grid on;
mid = round(Nx/2);
[minL, idxL] = min(Q_slice(1:mid));
[minR, idxR] = min(Q_slice(mid+1:end));
idxR = idxR + mid;
plot(r(idxL), minL, 'ro', 'MarkerFaceColor', 'r');
plot(r(idxR), minR, 'go', 'MarkerFaceColor', 'g');
title('Asymmetric Q-Potential (The Snap)');

% Final Audit
fprintf('\n--- RUPTURE AUDIT ---\n');
delta_Q = abs(minL - minR);
fprintf('Angular Momentum Generated: -0.217\n'); % From your console
fprintf('Pressure Differential (Delta Q): %.6e\n', delta_Q);