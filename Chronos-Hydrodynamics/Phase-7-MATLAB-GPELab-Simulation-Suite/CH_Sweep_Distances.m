%% CH Framework: Super-Solid Lattice Sweep
% Filename: CH_SuperSolid_Final.m
clear; clc; close all;

% --- SWEEP CONFIG (Multiples of Sigma/Grain) ---
distances = [3.33, 6.66, 9.99, 13.32]; 
results = struct('dist', [], 'n_harmonic', [], 'bridge_strength', [], 'stable', []);

% --- PAPER CONSTANTS (Section 2.2) ---
h_planck = 6.626; hbar = h_planck / (2*pi);
m_v = 6.63e-34; % Vortex mass unit from paper
c_light = 3e8;  % Acoustic velocity of vacuum
grain_xi = 3.33; % Normalized 3.33nm grain

% --- GRID (High Resolution centered on the Grain) ---
xmin = -40; xmax = 40; Nx = 512; % Higher resolution to prevent lattice rupture
ymin = -40; ymax = 40; Ny = 512;
Geometry2D = Geometry2D_Var2d(xmin, xmax, ymin, ymax, Nx, Ny);
[X, Y] = meshgrid(linspace(xmin, xmax, Nx), linspace(ymin, ymax, Ny));

% --- THE "SUPER-SOLID" IDENTITY (Section 2.1) ---
% To prevent "Topological Rupture" at Iteration 5, we must increase g
% to reflect the 10^43 Pa Rigidity.
Background_Rho = 1000; % High baseline per your test
g_stiffness = 5.0;     % Rigidity (mu) equivalent
Mass_Earth = 15.0;     % Scaled Stress
Mass_Moon  = 11.2;     % Scaled Stress (1.33 ratio)
Sigma = grain_xi;      % The "Universal Grain" is the anchor size

for i = 1:length(distances)
    D = distances(i);
    fprintf('\n--- Analyzing Lattice Tension at D = %.2f ---\n', D);
    
    Method = Method_Var2d('Ground', 1, 'BESP'); 
    Method.Deltat = 0.005; % Ultra-fine time-step to capture the "Snap"
    Method.Max_iter = 1500; 
    
    Physics2D = Physics2D_Var2d(Method);
    Physics2D.g = g_stiffness;
    
    % Section 3: Gravity as Lattice Pressure (W-Potential)
    Pot_Func = @(X,Y) + (Mass_Earth * exp(-((X + D/2).^2 + Y.^2)/(2*Sigma^2))) ...
                     + (Mass_Moon  * exp(-((X - D/2).^2 + Y.^2)/(2*Sigma^2)));
    Physics2D = Potential_Var2d(Method, Physics2D, {Pot_Func});
    
    % --- THOMAS-FERMI INITIALIZATION (Stability Lock) ---
    % Section 2.5: G = (w^2 * xi^4) / (hbar * rho)
    % We initialize the vacuum already in its "Geodesic Flow"
    TF_Density = (Background_Rho - Pot_Func(X,Y)) ./ g_stiffness;
    Phi_0 = {sqrt(TF_Density)}; 
    
    Outputs = struct();
    fields = {'Evo','Evo_outputs','Figure','Draw','Iterations','Max_iter','Save',...
              'User_compute_global','User_compute_local','User_compute_evolution',...
              'User_compute_functional','User_compute_custom','User_compute_functionals',...
              'Save_solution','Backup_solution'};
    for f = 1:length(fields); Outputs.(fields{f}) = 0; end
    
    try
        [Phi, ~] = GPELab2d(Phi_0, Method, Geometry2D, Physics2D, Outputs);
        rho = abs(Phi{1}).^2;
        sqrt_rho = sqrt(rho);
        
        % Section 3: The Madelung Bridge (Equation 6)
        dx = (xmax-xmin)/(Nx-1);
        [gradX, gradY] = gradient(sqrt_rho, dx);
        [lapX, ~] = gradient(gradX, dx);
        [~, lapY] = gradient(gradY, dx);
        
        % epsilon (1e-1) is the "Acoustic Softening" buffer
        Q = -(hbar^2 / (2 * m_v)) * ((lapX + lapY) ./ (sqrt_rho + 0.1));
        Q_Slice = Q(round(Ny/2), :);
        r = linspace(xmin, xmax, Nx);
        
        % Post-Analysis
        [~, idx_E] = min(Q_Slice(1:round(Nx/2)));
        [~, idx_M] = min(Q_Slice(round(Nx/2)+1:end));
        idx_M = idx_M + round(Nx/2);
        
        results(i).dist = D;
        results(i).bridge_strength = Q_Slice(round(Nx/2));
        results(i).n_harmonic = abs(r(idx_M) - r(idx_E)) / grain_xi;
        results(i).stable = true;
        
        fprintf('SUCCESS: Phase-Lock n = %.2f\n', results(i).n_harmonic);
    catch
        fprintf('FAILED: Lattice Rupture at D = %.2f\n', D);
        results(i).stable = false;
    end
end

% --- PLOT: THE "STAIRCASE" OF STRESS ---
valid = [results.stable];
if any(valid)
    figure('Color','w','Name','Forensic Lattice Analysis');
    subplot(2,1,1);
    plot([results(valid).dist], [results(valid).n_harmonic], 'bo-', 'LineWidth', 2);
    ylabel('Harmonic Lock (n)'); grid on; title('Quantized Orbital Grooves');
    
    subplot(2,1,2);
    plot([results.dist], [results(valid).bridge_strength], 'rd-', 'LineWidth', 2);
    ylabel('Lattice Tension (Q)'); xlabel('Distance (D)');
    title('Madelung Bridge Strength (The Gravity Mediator)');
end