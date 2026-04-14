%% CH Framework: Final Forensic Audit (Unified Master Script)
% Purpose: Validating SS-BEC Substrate Rigidity with Normalized Laboratory Waterfall
clear; clc; close all;

% --- CH CONSTANTS ---
h_planck = 6.626; m_vacuum = 6.630; hbar = h_planck / (2*pi);
grain_size = 3.33; 
xmin = -30; xmax = 30; Nx = 128; ymin = -30; ymax = 30; Ny = 128; 
Geometry2D = Geometry2D_Var2d(xmin, xmax, ymin, ymax, Nx, Ny);

% --- METHOD ---
Method = Method_Var2d('Ground', 1, 'BESP'); 
Method.Deltat = 0.05; Method.Is_Normalized = 0; Method.Max_iter = 2000; 

% --- PHYSICS ---
Physics2D = Physics2D_Var2d(Method);
Physics2D.g = 20000; 
Mass_Strength = 2.0; Radius_Earth = 3.33;        
Earth_Func = @(X,Y) +Mass_Strength * exp(-(X.^2 + Y.^2)/(2*Radius_Earth^2));
Physics2D = Potential_Var2d(Method, Physics2D, {Earth_Func});

% --- OUTPUTS ---
Outputs = struct();
fields = {'User_compute_global', 'User_compute_local', 'User_compute_evolution', ...
          'User_compute_functional', 'User_compute_custom', 'User_compute_functionals', ...
          'Save', 'Evo', 'Evo_outputs', 'Evo_functionals', 'Figure', 'Draw', ...
          'Solution_name', 'Backup_solution', 'Save_solution', 'Iterations', 'Max_iter'};
for i = 1:length(fields); Outputs.(fields{i}) = 0; end
Outputs.Iterations = 0; Outputs.Max_iter = 2000; Outputs.Evo_outputs = 500;  
Outputs.Evo = 1; Outputs.Figure = 1; Outputs.Draw = 1; Outputs.Solution_name = 'CH_Final_Audit';

% --- STAGE 1: INITIAL STABILIZATION ---
Phi_0 = {sqrt(50) * ones(Nx, Ny)}; 
fprintf('Launching Stabilized Audit. Stiffness g=%d...\n', Physics2D.g);
[Phi, ~] = GPELab2d(Phi_0, Method, Geometry2D, Physics2D, Outputs);

% --- POST-ANALYSIS (RAW vs SMOOTHED) ---
Phi_Final = Phi{1}; rho = abs(Phi_Final).^2; sqrt_rho = sqrt(rho);
r = linspace(xmin, xmax, Nx);
dx = (xmax-xmin)/(Nx-1); dy = (ymax-ymin)/(Ny-1);
[gradX, ~] = gradient(sqrt_rho, dx, dy); [lapX, ~] = gradient(gradX, dx, dy);
[~, gradY] = gradient(sqrt_rho, dx, dy); [~, lapY] = gradient(gradY, dx, dy);
Q_Raw = -(hbar^2 / (2 * m_vacuum)) * ((lapX + lapY) ./ (sqrt_rho + 1e-5));
Q_slice_raw = Q_Raw(Nx/2, :);
Q_slice_smooth = smoothdata(Q_slice_raw, 'gaussian', 15);
[~, minIdx] = min(Q_slice_smooth);
trough_x_base = r(minIdx);
harmonic_n_base = abs(trough_x_base) / grain_size;

% FIGURE 101: The Emergence Proof
figure(101); clf; set(gcf, 'Color', 'w', 'Name', 'CH Correspondence Audit');
plot(r, Q_slice_raw, 'Color', [0.7 0.7 0.7], 'LineWidth', 1, 'DisplayName', 'Quantum Lattice (Raw)'); 
hold on; plot(r, Q_slice_smooth, 'r', 'LineWidth', 2.5, 'DisplayName', 'Einsteinian Limit (Smoothed)');
grid on; title('Emergent Gravity: Substrate Ripples vs. Mean-Field Well');
legend; xlabel('Radial Distance'); ylabel('Q-Potential'); shg;

%% --- STAGE 2: RIGIDITY AUDIT (UNIFIED WATERFALL) ---
fprintf('\n--- STARTING RIGIDITY AUDIT ---\n');
Mass_Tests = [2.0, 4.0, 8.0]; Results_X = zeros(size(Mass_Tests));
Q_Storage_Raw = zeros(length(Mass_Tests), Nx); 

for m = 1:length(Mass_Tests)
    Temp_Earth = @(X,Y) +Mass_Tests(m) * exp(-(X.^2 + Y.^2)/(2*Radius_Earth^2));
    Physics2D = Potential_Var2d(Method, Physics2D, {Temp_Earth});
    [Phi_A, ~] = GPELab2d(Phi_0, Method, Geometry2D, Physics2D, Outputs);
    rho_a = abs(Phi_A{1}).^2; [gX_a, ~] = gradient(sqrt(rho_a), dx, dy); [lX_a, ~] = gradient(gX_a, dx, dy);
    Q_loop_raw = -(hbar^2 / (2 * m_vacuum)) * (lX_a ./ (sqrt(rho_a) + 1e-5));
    Q_Storage_Raw(m, :) = Q_loop_raw(Nx/2, :);
    Q_S = smoothdata(Q_loop_raw(Nx/2, :), 'gaussian', 15);
    [~, mIdx] = min(Q_S); Results_X(m) = r(mIdx);
    fprintf('Mass: %.1f | Trough X: %.4f\n', Mass_Tests(m), Results_X(m));
end

% FIGURE 102: Rigidity Waterfall (Normalized & Annotated)
figure(102); clf; set(gcf, 'Color', 'w', 'Name', 'Rigidity Waterfall Audit'); hold on;
clrs = [0 0.447 0.741; 0.85 0.325 0.098; 1 0 0]; % Professional color set
offsets = [0.8, 0.4, 0]; % Stacked layout

for m = 1:length(Mass_Tests)
    % Normalize and smooth for the visual baseline
    Q_trace = Q_Storage_Raw(m, :);
    Q_norm = Q_trace / max(abs(Q_trace)); 
    Q_vis_smooth = smoothdata(Q_norm, 'gaussian', 15);
    
    % Plot raw spiky trace in light color, smoothed trace in bold
    plot(r, Q_norm + offsets(m), 'Color', [clrs(m,:) 0.3], 'LineWidth', 0.5, 'HandleVisibility', 'off');
    plot(r, Q_vis_smooth + offsets(m), 'Color', clrs(m,:), 'LineWidth', 2, 'DisplayName', ['Mass ' num2str(Mass_Tests(m))]);
    
    % Plot the Diamond Marker at the trough
    [~, mIdx] = min(Q_vis_smooth);
    plot(r(mIdx), -1 + offsets(m), 'kd', 'MarkerFaceColor', clrs(m,:), 'MarkerSize', 8, 'HandleVisibility', 'off');
    text(r(mIdx), -1 + offsets(m) - 0.08, sprintf('X=%.2f', r(mIdx)), 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
end

xline(Results_X(1), '--k', 'Lattice Pinning Reference', 'LabelVerticalAlignment', 'top');
grid on; title('Stage 2 Rigidity Audit: Substrate Pinning vs. Rupture');
xlabel('Radial Coordinate'); ylabel('Normalized Q-Potential (Stacked)');
legend('show'); shg;

%% --- STAGE 3: HYSTERESIS AUDIT ---
fprintf('\n--- STARTING TOPOLOGICAL HYSTERESIS AUDIT ---\n');
Hysteresis_Mass = [2.0, 8.0, 2.0]; H_Results = zeros(size(Hysteresis_Mass)); Phi_H = Phi; 
for h = 1:length(Hysteresis_Mass)
    Temp_Func = @(X,Y) +Hysteresis_Mass(h) * exp(-(X.^2 + Y.^2)/(2*Radius_Earth^2));
    Physics2D = Potential_Var2d(Method, Physics2D, {Temp_Func});
    [Phi_H, ~] = GPELab2d(Phi_H, Method, Geometry2D, Physics2D, Outputs); 
    rho_h = abs(Phi_H{1}).^2; [gX_h, ~] = gradient(sqrt(rho_h), dx, dy); [lX_h, ~] = gradient(gX_h, dx, dy);
    Q_h_raw = -(hbar^2 / (2 * m_vacuum)) * (lX_h ./ (sqrt(rho_h) + 1e-5));
    Q_h_s = smoothdata(Q_h_raw(Nx/2, :), 'gaussian', 15);
    [~, mIdx_h] = min(Q_h_s); H_Results(h) = r(mIdx_h);
end

% FIGURE 103: Hysteresis Memory Loop
figure(103); clf; set(gcf, 'Color', 'w', 'Name', 'Hysteresis Memory Audit');
plot(Hysteresis_Mass, H_Results, '-ok', 'LineWidth', 2, 'MarkerFaceColor', 'r', 'MarkerSize', 8);
hold on; grid on;
line([Hysteresis_Mass(1), Hysteresis_Mass(3)], [H_Results(1), H_Results(3)], 'Color', 'b', 'LineStyle', '--', 'LineWidth', 2);
text(Hysteresis_Mass(1)+0.5, (H_Results(1)+H_Results(3))/2, 'MEMORY GAP', 'Color', 'b', 'FontWeight', 'bold');
title('Topological Hysteresis: Vacuum Memory Audit');
xlabel('Mass Stress (M)'); ylabel('Trough Position (X)'); shg;

% Final Narrative Output
fprintf('\n--- CH FINAL AUDIT COMPLETE ---\n');
fprintf('Base Harmonic n: %.4f\n', harmonic_n_base);
fprintf('Permanent Memory Shift: %.4f units\n', H_Results(3) - H_Results(1));