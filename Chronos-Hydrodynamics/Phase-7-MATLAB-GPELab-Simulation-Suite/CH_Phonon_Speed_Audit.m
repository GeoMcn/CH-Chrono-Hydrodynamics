%% CH Framework: Phonon Speed Audit (Master Multi-Peak Analysis)
% Filename: CH_Phono_Speed_Audit_Master.m
clear; clc; close all;

% --- CH CONSTANTS ---
h_planck = 6.626; hbar = h_planck / (2*pi); m_vacuum = 6.630;
xmin = -40; xmax = 40; Nx = 256; 
ymin = -40; ymax = 20; Ny = 256; % Note: Matches your grid geometry
Geometry2D = Geometry2D_Var2d(xmin, xmax, ymin, ymax, Nx, Ny);

% --- METHOD: DYNAMIC ---
Method = Method_Var2d('Dynamic', 1, 'BESP'); 
Method.Deltat = 0.001; 
Method.Max_iter = 100; 
Method.Print = 0;
Physics2D = Physics2D_Var2d(Method);
Physics2D.g = 20000; % High-Rigidity 2009 Phase

% --- INITIAL UNIFORM VACUUM ---
Phi_0 = {sqrt(10) * ones(Nx, Ny)}; 
mid = Nx/2;
[X, Y] = meshgrid(linspace(xmin, xmax, Nx), linspace(ymin, ymax, Ny));
Pulse = 5.0 * exp(-(X.^2 + Y.^2)/(2*0.5^2)); 
Phi_Kick = Phi_0{1} + Pulse;

% --- TOTAL SATIATION BLOCK (Long-Form Stable) ---
Outputs = struct();
f = {'User_compute_global','User_compute_local','User_compute_evolution',...
     'User_compute_functional','User_compute_custom','User_compute_functionals',...
     'Save','Evo','Evo_outputs','Evo_functionals','Figure','Draw',...
     'Solution_name','Backup_solution','Save_solution'};
for i=1:length(f); Outputs.(f{i})=0; end;

dummy_vec = {zeros(1, 2000)}; 
Outputs.phi_abs_0 = dummy_vec;
Outputs.x_rms = dummy_vec;    
Outputs.y_rms = dummy_vec;
Outputs.energy = dummy_vec;
Outputs.Energy = dummy_vec;
Outputs.chemical_potential = dummy_vec;
Outputs.Chemical_potential = dummy_vec;
Outputs.stopping_criterion = dummy_vec;
Outputs.Stopping_criterion = dummy_vec;
Outputs.angular_momentum = dummy_vec; 
Outputs.Angular_momentum = dummy_vec; 
Outputs.Iterations = 1;
Outputs.Max_iter = 100;

% --- EXECUTION ---
fprintf('Launching Gravitational Pulse (g=20,000)... ');
[Phi_Final, ~] = GPELab2d({Phi_Kick}, Method, Geometry2D, Physics2D, Outputs);
fprintf('Done.\n');

% --- MEASURE PROPAGATION ---
rho_end = abs(Phi_Final{1}).^2;
rho_start = abs(Phi_Kick).^2;
diff_map = rho_end - rho_start; 
r_axis = linspace(0, xmax, Nx/2);
slice = diff_map(mid, mid+1:end);

% MULTI-PEAK EXTRACTION
% This finds all peaks in the 'heartbeat' signal
[pks, locs] = findpeaks(slice, 'MinPeakDistance', 2);
[mainPeakVal, mainIdx] = max(slice);
dist_at_main = r_axis(mainIdx);

% --- VISUALIZATION ---
figure('Color', 'w', 'Position', [100, 100, 1100, 500]);
subplot(1,2,1);
imagesc(linspace(xmin, xmax, Nx), linspace(ymin, ymax, Ny), diff_map);
axis square; colormap(jet); colorbar;
title('Phonon (Gravity) Wavefront Map');
xlabel('X'); ylabel('Y');

subplot(1,2,2);
plot(r_axis, slice, 'b', 'LineWidth', 2); hold on;
% Mark the Primary Wavefront (Information Speed)
plot(dist_at_main, mainPeakVal, 'ro', 'MarkerSize', 10, 'MarkerFaceColor', 'r');
% Mark the Lattice Echoes (Secondary Peaks)
if ~isempty(locs)
    plot(r_axis(locs), pks, 'gd', 'MarkerSize', 6);
end
grid on;
xlabel('Distance (Lattice Units)'); ylabel('\Delta Density');
legend('Waveform Profile', 'Leading Peak (Signal)', 'Secondary Peaks (Echo)');
title(['Measured Speed v_p = ', num2str((dist_at_main/(Method.Deltat*Method.Max_iter)), '%.4f')]);

% --- FINAL CONSOLE AUDIT ---
fprintf('\n--- COMPREHENSIVE PHONON AUDIT ---\n');
fprintf('PRIMARY SIGNAL COORDINATES:\n');
fprintf('  X (Distance): %.6f units\n', dist_at_main);
fprintf('  Y (Amplitude): %.6f\n', mainPeakVal);

fprintf('\nLATTICE ECHO COORDINATES (Trailing Ripples):\n');
for i = 1:min(length(pks), 5)
    fprintf('  Peak %d -> X: %.6f | Y: %.6f\n', i, r_axis(locs(i)), pks(i));
end

v_phonon = dist_at_main / (Method.Deltat * Method.Max_iter);
fprintf('\n--- SPEED SUMMARY ---\n');
fprintf('Measured Phonon Speed: %.4f units/sec\n', v_phonon);
fprintf('Relative to Light (c=1.25): %.2fx\n', v_phonon / 1.25);