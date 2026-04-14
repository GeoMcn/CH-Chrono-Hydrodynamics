# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import os

def find_audit_file(filename):
    """
    Search Priority:
    1. Current script directory.
    2. One level up -> 'Data' folder -> recursive search.
    """
    current_dir = pathlib.Path(__file__).parent.resolve()
    
    # 1. Local Search
    local_path = current_dir / filename
    if local_path.exists():
        print(f"[System] Source file found locally: {local_path}")
        return local_path
    
    # 2. ../Data Recursive Search
    data_dir = current_dir.parent / "Data"
    if data_dir.exists():
        for path in data_dir.rglob(filename):
            if path.is_file():
                print(f"[System] Source file found in archive: {path}")
                return path
                
    return None

def run_full_energy_audit(input_filename):
    # Resolve the path using the new logic
    input_file = find_audit_file(input_filename)
    
    if not input_file:
        print(f"ERROR: File '{input_filename}' not found in local dir or ../Data/ tree.")
        return

    # --- 1. DATA RELOAD ---
    df = pd.read_csv(input_file)
    df.columns = [c.strip().upper() for c in df.columns]
    
    # --- 2. RAW RESIDUAL EXTRACTION (CM scaling) ---
    # Using 'X' as the primary residual column for G25
    df['JITTER'] = df['X'].abs() * 100

    # --- 3. DYNAMIC YEAR EXTRACTION ---
    df['YEAR'] = df['TIMESTAMP'].str.split('_').str[0]
    years = sorted(df['YEAR'].unique(), key=int)

    # --- 4. THE COMPREHENSIVE REPORT ---
    threshold = 50 
    print("\n" + "="*85)
    print(f"SECTION 10.0: MULTI-DECADAL VACUUM ENERGY PEAK ANALYSIS (2000-{years[-1]})")
    print(f"DIAGNOSTIC ENGINE: vacuum_lattice_rupture_audit.py")
    print("="*85)
    print(f"{'YEAR':<6} | {'POP':<8} | {'MAX JITTER':<12} | {'TOP 3 MEAN':<12} | {'RUPTURES'}")
    print("-" * 85)
    
    plot_data = []
    labels = []
    
    for year in years:
        v_year = df[df['YEAR'] == year]['JITTER'].values
        if len(v_year) == 0: continue
        
        top_3 = sorted(v_year)[-3:]
        max_j = np.max(v_year)
        mean_top = np.mean(top_3)
        ruptures = np.sum(v_year > threshold)
        
        plot_data.append(v_year)
        labels.append(year)
        
        print(f"{year:<6} | {len(v_year):<8} | {max_j:<12.2f} | {mean_top:<12.2f} | {ruptures} (>50cm)")

    # --- 5. THE "WIGGLE TO STOP" QUANTIFICATION ---
    baseline_peak = np.max(df[df['YEAR'] == years[0]]['JITTER'])
    modern_peak = np.max(df[df['YEAR'] == years[-1]]['JITTER'])
    
    print("-" * 85)
    print(f"Baseline Peak ({years[0]}): {baseline_peak:.2f} cm")
    print(f"Modern Peak ({years[-1]}):   {modern_peak:.2f} cm")
    print(f"Total Suppression Delta:    {modern_peak - baseline_peak:.2f} cm")
    print("="*85)

    # --- 6. THE PHASE TRANSITION VISUALIZATION ---
    plt.figure(figsize=(16, 8), dpi=150)
    
    colors = []
    for y in years:
        y_int = int(y)
        if y_int <= 2003: colors.append('#2ca02c')   # Green: Laminar
        elif 2004 <= y_int <= 2007: colors.append('#ff7f0e') # Orange: Strain
        elif y_int == 2008: colors.append('#d62728') # Red: Rupture
        elif y_int == 2009: colors.append('#9467bd') # Purple: Snap
        else: colors.append('#1f77b4')               # Blue: Crystalline

    bp = plt.boxplot(plot_data, tick_labels=labels, patch_artist=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    plt.yscale('log')
    plt.axhline(y=threshold, color='black', linestyle='--', alpha=0.3, label='Forensic Threshold')
    
    plt.title(f"Vacuum Lattice Phase Transition History ({years[0]}-{years[-1]})", fontsize=14)
    plt.ylabel("Jitter Magnitude (cm) [Log Scale]", fontsize=12)
    plt.xlabel("Forensic Year", fontsize=12)
    plt.grid(True, which="both", ls="-", alpha=0.1)
    
    # Custom Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#2ca02c', lw=4, label='Laminar Baseline'),
        Line2D([0], [0], color='#ff7f0e', lw=4, label='Strain Buildup'),
        Line2D([0], [0], color='#d62728', lw=4, label='Peak Rupture (Vice-Grip)'),
        Line2D([0], [0], color='#9467bd', lw=4, label='Phase Snap'),
        Line2D([0], [0], color='#1f77b4', lw=4, label='Crystalline Stasis')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Updated filename for consistency with paper
    plt.savefig("peak-energy-analysis-2000-2022.png", dpi=300)
    plt.show()

# Run the full forensic sweep
run_full_energy_audit("G25_Full_Timeline_2000_2022_Audit.csv")
# %%