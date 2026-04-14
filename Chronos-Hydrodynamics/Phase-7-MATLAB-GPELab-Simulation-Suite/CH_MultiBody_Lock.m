%% CH Framework: Multi-Body Phase-Locking (Visual Forensics - Fail-Safe)
% Filename: CH_MultiBody_VisualForensics_Final.m
clear; clc; close all;

% --- CH CONSTANTS ---
h_planck = 6.626; hbar = h_planck / (2*pi); m_vacuum = 6.630;
grain_size = 3.33; 
xmin = -40; xmax = 40; Nx = 256; 
ymin = -40; ymax = 40; Ny = 256;
Geometry2D = Geometry2D_Var2d(xmin, xmax, ymin, ymax, Nx, Ny);

% --- METHOD CONFIG ---
Method = Method_Var2d('Ground', 1, 'BESP'); 
Method.Deltat = 0.05; 
Method.Max_iter = 8500; 

% --- THE PHASE-LOCK CALIBRATION ---
Physics2D = Physics2D_Var2d(Method);
Physics2D.g = 0.0005;    
Mass_Earth = 110.00;     
Mass_Moon  = 82.00;      
Sigma = 1.8;             

Multi_Body_Func = @(X,Y) + (Mass_Earth * exp(-(X.^2 + Y.^2)/(2*Sigma^2))) ...
                         + (Mass_Moon * exp(-((X-3.4).^2 + Y.^2)/(2*Sigma^2)));

Physics2D = Potential_Var2d(Method, Physics2D, {Multi_Body_Func});

% --- FAIL-SAFE OUTPUT STRUCTURE ---
% We manually define every field to ensure the solver doesn't crash
Outputs = struct();
Outputs.Evo = 0;
Outputs.Evo_outputs = 100;
Outputs.Figure = 0;
Outputs.Draw = 0;
Outputs.Iterations = 0;
Outputs.Max_iter = Method.Max_iter;
Outputs.Save = 0;
Outputs.User_compute_global = 0;
Outputs.User_compute_local = 0;
Outputs.User_compute_evolution = 0;
Outputs.User_compute_functional = 0;
Outputs.User_compute_custom = 0;
Outputs.User_compute_functionals = 0; % Added the plural version just in case
Outputs.Save_solution = 0;
Outputs.Backup_solution = 0;
Outputs.Solution_name = 'bridge';
Outputs.phi_abs_0 = {0};
Outputs.energy = {0};
Outputs.chemical_potential = {0};
Outputs.stopping_criterion = {0};
Outputs.x_rms = {0};
Outputs.y_rms = {0};

% --- INITIAL STATE ---
Density_Val = 40;
Phi_0 = {sqrt(Density_Val) * ones(Nx, Ny)}; 

% --- RUN SIMULATION ---
fprintf('Executing Fail-Safe Visual Forensics (n=3.33 Snap)...\n');
[Phi, ~] = GPELab2d(Phi_0, Method, Geometry2D, Physics2D, Outputs);

% --- POST-SIMULATION FORENSIC ANALYSIS ---
Phi_Final = Phi{1};
rho = abs(Phi_Final).^2; 
sqrt_rho = sqrt(rho);
r = linspace(xmin, xmax, Nx);
dx = (xmax-xmin)/(Nx-1); dy = (ymax-ymin)/(Ny-1);
[gradX, gradY] = gradient(sqrt_rho, dx, dy);
[lapX, ~] = gradient(gradX, dx, dy);
[~, lapY] = gradient(gradY, dx, dy);

% Equation 6: Emergent Gravity (Quantum Potential Q)
Q_Final = -(hbar^2 / (2 * m_vacuum)) * ((lapX + lapY) ./ (sqrt_rho + 1e-2));

% Slice analysis for the Bridge Profile
Q_Slice = Q_Final(round(Ny/2), :);
[minVal_Earth, idx_E] = min(Q_Slice(1:round(Nx/2)));
[minVal_Moon, idx_M] = min(Q_Slice(round(Nx/2)+1:end));
idx_M = idx_M + round(Nx/2);
Saddle_Point_Val = Q_Slice(round((idx_E + idx_M)/2));

% --- ENHANCED VISUALIZATION SUITE ---
hFig = figure('Name', 'CH Forensic Dashboard', 'Color', 'w', 'Position', [50, 50, 1200, 800]);

% 1. TOP-DOWN TOPOLOGY
subplot(2,2,1);
imagesc(r, r, Q_Final); axis square; colormap(jet); colorbar;
hold on;
plot(r(idx_E), 0, 'wo', 'MarkerSize', 10, 'LineWidth', 2); 
plot(r(idx_M), 0, 'wx', 'MarkerSize', 10, 'LineWidth', 2); 
caxis([min(Q_Final(:)) 0.001]);
title('Top-Down: Gravity Bridge');

% 2. THE SOLID MANIFOLD (Smoothed Surface)
subplot(2,2,2);
s = surf(r, r, Q_Final);
s.EdgeColor = 'none'; % This removes the grid lines
view(-35, 45); camlight; lighting gouraud; colormap(jet);
title('3D: Phase-Locked Surface');

% 3. THE BRIDGE PROFILE (Side View)
subplot(2,2,3);
plot(r, Q_Slice, 'b', 'LineWidth', 2);
hold on; grid on;
plot(r(idx_E), minVal_Earth, 'ro', 'MarkerFaceColor', 'r');
plot(r(idx_M), minVal_Moon, 'ro', 'MarkerFaceColor', 'r');
title('1D: Bridge Cross-Section');
xlabel('Distance'); ylabel('Q Potential');

% 4. VACUUM DENSITY MAP
subplot(2,2,4);
imagesc(r, r, rho); axis square; colormap(parula); colorbar;
title('Density (Vacuum Displacement)');

fprintf('\n--- FORENSIC SNAPSHOT ---\n');
fprintf('n-Harmonic: %.4f\n', abs(r(idx_M))/grain_size);
fprintf('Bridge Strength: %.4e\n', Saddle_Point_Val);