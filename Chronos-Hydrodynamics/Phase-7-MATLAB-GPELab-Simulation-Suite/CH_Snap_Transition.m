%% CH Framework: Dynamic Phase-Transition Simulation (The 2009 Snap)
% Filename: CH_Snap_Transition.m
% Purpose: Proving the "Elastic Rebound" from Metastable n=2.62 to Integer n=3.0
clear; clc; close all;

% --- CH CONSTANTS ---
h_planck = 6.626; hbar = h_planck / (2*pi); m_vacuum = 6.630;
grain_size = 3.33; % xi (Universal Grain Size)
xmin = -30; xmax = 30; Nx = 128;
ymin = -30; ymax = 30; Ny = 128;
Geometry2D = Geometry2D_Var2d(xmin, xmax, ymin, ymax, Nx, Ny);

% --- DYNAMIC METHOD CONFIG ---
Method = Method_Var2d('Ground', 1, 'BESP'); 
Method.Deltat = 0.05; 
Method.Max_iter = 5000; 

% --- INITIAL PHYSICS ---
Physics2D = Physics2D_Var2d(Method);
Physics2D.g = 20000; 
Mass_Strength = 2.0;
Radius_Earth = 3.33;
Earth_Func = @(X,Y) +Mass_Strength * exp(-(X.^2 + Y.^2)/(2*Radius_Earth^2));
Physics2D = Potential_Var2d(Method, Physics2D, {Earth_Func});

% --- DYNAMIC STIFFNESS FUNCTION (The Rebound Trigger) ---
Physics2D.Control_g = @(iter) (iter < 2500) * 20000 + (iter >= 2500) * 10000;

% --- OUTPUTS ---
Outputs = struct();
fields = {'User_compute_global', 'User_compute_local', 'User_compute_evolution', ...
          'User_compute_functional', 'User_compute_custom', 'User_compute_functionals', ...
          'Save', 'Evo', 'Evo_outputs', 'Evo_functionals', 'Figure', 'Draw', ...
          'Solution_name', 'Backup_solution', 'Save_solution', 'Iterations', 'Max_iter'};
for i = 1:length(fields); Outputs.(fields{i}) = 0; end
Outputs.Evo = 1; Outputs.Evo_outputs = 250; 
Outputs.Figure = 1; Outputs.Draw = 1;

% --- INITIAL STATE ---
Phi_0 = {sqrt(50) * ones(Nx, Ny)}; 
fprintf('Launching Long-Duration Snap Simulation...\n');
[Phi, Final_Outputs] = GPELab2d(Phi_0, Method, Geometry2D, Physics2D, Outputs);

% --- POST-SNAP ANALYSIS ---
Phi_Final = Phi{1};
rho = abs(Phi_Final).^2;
sqrt_rho = sqrt(rho);
r = linspace(xmin, xmax, Nx);
dx = (xmax-xmin)/(Nx-1); dy = (ymax-ymin)/(Ny-1);

[gradX, gradY] = gradient(sqrt_rho, dx, dy);
[lapX, ~] = gradient(gradX, dx, dy);
[~, lapY] = gradient(gradY, dx, dy);

Q_Final = -(hbar^2 / (2 * m_vacuum)) * ((lapX + lapY) ./ (sqrt_rho + 1e-5));
Q_Smooth = smoothdata(Q_Final(Nx/2, :), 'gaussian', 15);

[minVal, minIdx] = min(Q_Smooth);
trough_x_final = r(minIdx);
n_final = abs(trough_x_final) / grain_size;

% --- FINAL FORENSIC VISUALIZATION ---
hFig = figure('Name', 'CH Forensic Audit: Phase-Locking Validation', 'Color', 'w', 'Position', [100, 100, 1200, 500]);

% Subplot 1: Radial Profile (The Harmonic Locking)
subplot(1,2,1);
plot(r, Q_Smooth, 'b', 'LineWidth', 3); hold on;
grid on;
% Draw the Harmonic Target Lines
xline(grain_size * 1, ':k', 'n=1');
xline(grain_size * 2, ':k', 'n=2');
xline(grain_size * 3, '--r', 'n=3 Harmonic Target', 'LineWidth', 1.5);
% Plot the actual measured trough
plot(trough_x_final, minVal, 'ro', 'MarkerSize', 10, 'MarkerFaceColor', 'r');

title(['Radial Potential: Final n = ', num2str(n_final, '%.3f')]);
xlabel('Radial Distance (X)'); ylabel('Q Strength');
legend('Smoothed Gravity Well', 'Lattice Nodes', '', 'n=3 Target Groove', 'Measured Trough');

% Subplot 2: 2D Field Visualization (The W-Well Geometry)
subplot(1,2,2);
imagesc(r, r, Q_Final); 
axis square; colormap(parula); colorbar;
caxis([-1 0.5]); % Constrain color for contrast
title('Top-Down Potential Topology');
xlabel('X-Axis'); ylabel('Y-Axis');

fprintf('\n--- CH DYNAMIC SNAP RESULTS ---\n');
fprintf('Final Trough Position: %.4f\n', trough_x_final);
fprintf('Final Harmonic Node (n): %.4f\n', n_final);
shg;