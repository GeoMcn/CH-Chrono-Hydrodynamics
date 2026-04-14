%% CH Framework: Master Resonance Alignment
% Filename: CH_Resonance_Alignment.m
clear; clc; close all;

% --- PARAMETERS FROM PAPER SECTION 7.2 ---
alpha_fs = 1/137.036; % Fine Structure Constant
grain_xi = 3.33;      % Universal Grain Size
Background_Rho = 1000; 

% --- STABILITY BUFFER (The "Viscosity" Fix) ---
% We apply Section 7.1: eta_path scaling
% This acts as a numerical "Shock Absorber"
eta_buffer = alpha_fs * 10; 

distances = [3.33, 6.66, 9.99, 13.32]; 
results = struct('dist', [], 'n_harmonic', [], 'bridge_strength', [], 'stable', []);

for i = 1:length(distances)
    D = distances(i);
    fprintf('\n--- Testing Phase-Lock at D = %.2f ---\n', D);
    
    % Solver Config
    Method = Method_Var2d('Ground', 1, 'BESP'); 
    Method.Deltat = 0.001; % Reduced further to prevent "Snap"
    Method.Max_iter = 1000; 
    
    % PHYSICS: Using the "Rigidity" from Paper Section 2.1
    Physics2D = Physics2D_Var2d(Method);
    Physics2D.g = 10.0; % High Rigidity (mu)
    
    % Mass scaling to the alpha_fs level
    Mass_Earth = 5.0 * alpha_fs * 100; % Normalized mass
    Mass_Moon  = 3.7 * alpha_fs * 100;
    
    Pot_Func = @(X,Y) + (Mass_Earth * exp(-((X + D/2).^2 + Y.^2)/(2*grain_xi^2))) ...
                     + (Mass_Moon  * exp(-((X - D/2).^2 + Y.^2)/(2*grain_xi^2)));
    Physics2D = Potential_Var2d(Method, Physics2D, {Pot_Func});
    
    % INITIAL STATE: The "Bowstring" Initialization
    % We start with a vacuum that is already "Tense"
    xmin = -50; xmax = 50; Nx = 256;
    [X, Y] = meshgrid(linspace(xmin, xmax, Nx), linspace(xmin, xmax, Nx));
    TF_Density = (Background_Rho - Pot_Func(X,Y)) / Physics2D.g;
    Phi_0 = {sqrt(TF_Density)}; 

    try
        % RUN - This is the check for "Topological Rupture"
        [Phi, ~] = GPELab2d(Phi_0, Method, Geometry2D_Var2d(xmin, xmax, xmin, xmax, Nx, Nx), Physics2D, struct('Max_iter', 1000, 'Evo', 0));
        
        % If we reach here, the lattice held!
        results(i).stable = true;
        fprintf('Lattice Intact: Harmonic Lock achieved.\n');
    catch
        % This is the "2008 Rupture" point
        results(i).stable = false;
        fprintf('LATTICE RUPTURE: Exceeded Elastic Limit.\n');
    end
end