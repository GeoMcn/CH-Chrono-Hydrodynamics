%% CH Framework: 2009 Storm Visualization (Wake Discovery)
clear; clc; close all;

% --- GRID ---
xmin = -20; xmax = 20; Nx = 128; ymin = -20; ymax = 20; Ny = 128;
Geometry2D = Geometry2D_Var2d(xmin, xmax, ymin, ymax, Nx, Ny);

% --- METHOD: Dynamic Evolution to see movement ---
Method = Method_Var2d('Dynamic', 1, 'BESP'); 
Method.Deltat = 0.005; 
Method.Max_iter = 200; % Let it run long enough to develop a wake
Method.Print = 0;

Physics2D = Physics2D_Var2d(Method);
Physics2D.g = 20000; 

% --- GALACTIC STORM (Super-Critical Velocity) ---
% We use a lower background density (sqrt(5)) to make ripples visible
v_storm = 8.0; 
Phi_0 = {sqrt(5) * exp(1i * v_storm * Geometry2D.X)}; 

% --- THE EARTH ---
Mass_Earth = 500; Sigma = 1.0;
Earth_Func = @(X,Y) Mass_Earth * exp(-(X.^2 + Y.^2)/(2*Sigma^2));
Physics2D = Potential_Var2d(Method, Physics2D, {Earth_Func});

% --- SATIATION ---
Outputs = struct();
f = {'User_compute_global','User_compute_local','User_compute_evolution','User_compute_functional','User_compute_custom','User_compute_functionals','Save','Evo','Evo_outputs','Evo_functionals','Figure','Draw','Solution_name','Backup_solution','Save_solution','Iterations','Max_iter'};
for i=1:length(f); Outputs.(f{i})=0; end; 
dummy = {zeros(1, 1001)};
Outputs.phi_abs_0 = dummy; Outputs.x_rms = dummy; Outputs.y_rms = dummy;
Outputs.Energy = dummy; Outputs.Chemical_potential = dummy;
Outputs.Angular_momentum = dummy; Outputs.Stopping_criterion = dummy;
Outputs.Iterations = 1;

fprintf('Visualizing the Galactic Wake... ');
[Phi, ~] = GPELab2d(Phi_0, Method, Geometry2D, Physics2D, Outputs);
fprintf('Done.\n');

% --- VISUALIZATION ---
% --- ENHANCED VISUALIZATION & DATA DUMP ---
rho = abs(Phi{1}).^2;
r = linspace(xmin, xmax, Nx);

% LOGARITHMIC SCALING (This makes faint ripples visible)
rho_log = log10(rho + 1e-6); 

figure('Color', 'w', 'Position', [100, 100, 1000, 500]);
subplot(1,2,1);
% We "clip" the display to focus on the wake, not the Earth's core
imagesc(r, r, rho_log, [-1, 2]); 
axis square; colormap(jet); colorbar;
title('Log-Scale Density (Looking for V-Wake)');

subplot(1,2,2);
% Take a slice behind the earth to see the "bumpy" wake
wake_slice = rho(round(Ny/2), round(Nx/2):end);
plot(wake_slice, 'LineWidth', 2); grid on;
title('Density Slice Behind Earth');

% --- THE DATA DUMP (Copy/Paste this to me) ---
fprintf('\n--- WAKE PATTERN DATA DUMP ---\n');
% We sample a 10x10 grid just behind the Earth (Center-right)
sample_zone = rho(60:70, 70:80); 
disp(sample_zone);
fprintf('--- END DUMP ---\n');
% --- ENERGY FLUX AUDIT ---
% Calculate the Poynting-like vector for the Vacuum Flow
[jx, jy] = gradient(Phi{1}.*conj(Phi{1})); % Probability current
Energy_Flux = real(jx + jy); 

figure('Color', 'w');
imagesc(r, r, Energy_Flux); colormap(jet); colorbar;
title('2009 Snap: Substrate Energy Flux');
% --- NUMERICAL ENERGY FLUX DUMP ---
% jx and jy represent the directional "push" of the vacuum
% j_total combines them to show the total magnitude of the energy flow
j_total = sqrt(jx.^2 + jy.^2);

% We sample the "Red" (High Flux) and "Blue" (Low Flux) regions
% These coordinates target the areas you described (Top and Bottom)
top_sample = j_total(round(Ny*0.25), round(Nx/2));    % The "Blue" Zone
bottom_sample = j_total(round(Ny*0.75), round(Nx/2)); % The "Red" Zone

fprintf('\n--- ENERGY FLUX MAGNITUDE AUDIT ---\n');
fprintf('Top Zone (Blue/Pull) Flux:   %.6e\n', top_sample);
fprintf('\nBottom Zone (Red/Push) Flux: %.6e\n', bottom_sample);

% Calculate the Flux Differential (The "Snap" Force)
flux_diff = abs(bottom_sample - top_sample);
fprintf('\nTotal Flux Differential:     %.6e\n', flux_diff);

% --- TEXT GRID DUMP ---
% Sampling a vertical slice through the Earth to see the Red-to-Blue transition
fprintf('\n--- VERTICAL FLUX CROSS-SECTION ---\n');
vertical_slice = j_total(40:88, round(Nx/2));
disp(vertical_slice');
fprintf('--- END DUMP ---\n');