# %%
import numpy as np
import glob
import os
import sys
import matplotlib.pyplot as plt
import pathlib
import pandas as pd

# --- DIRECTORY RESOLVER ---
def get_search_paths():
    """
    Returns a list of search patterns. 
    1. Current Directory
    2. ../Data/ recursively
    """
    script_dir = pathlib.Path(__file__).parent.resolve()
    parent_data_dir = script_dir.parent / "Data"
    
    # Pattern 1: Local folder
    patterns = [str(script_dir)]
    
    # Pattern 2: ../Data folder
    if parent_data_dir.exists():
        patterns.append(str(parent_data_dir / "**"))
    else:
        print(f"Warning: 'Data' folder not found at {parent_data_dir}")
        
    return patterns

# --- DUAL OUTPUT LOGGER ---
class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self): pass

def parse_igs_clock_data(file_path, prn_list):
    clock_data = {prn: [] for prn in prn_list}
    if not os.path.exists(file_path): return None

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if 'AS ' in line:
                parts = line.split()
                if len(parts) < 5: continue 
                prn_id = parts[1]
                if prn_id in prn_list:
                    for p in parts[5:]:
                        if 'E' in p.upper() or ('.' in p and len(p) > 10):
                            try:
                                val = float(p) * 1e9 
                                clock_data[prn_id].append(val)
                                break 
                            except ValueError: continue
    
    variances = {}
    for prn in prn_list:
        offsets = clock_data.get(prn, [])
        if len(offsets) > 10:
            residuals = np.diff(offsets, n=2) 
            variances[prn] = np.var(residuals)
        else:
            variances[prn] = 0.0
    return variances

def find_files(prefix_pattern):
    search_dirs = get_search_paths()
    all_found = []
    for s_dir in search_dirs:
        full_pattern = os.path.join(s_dir, prefix_pattern)
        all_found.extend(glob.glob(full_pattern, recursive=True))
    return all_found

def run_audit(label, file_list, prns):
    all_deltas = []
    unique_paths = sorted(list(set(file_list)))
    if not unique_paths: return 0.0
    for f in unique_paths:
        v = parse_igs_clock_data(f, prns)
        if v and v.get(prns[0], 0) > 0 and v.get(prns[1], 0) > 0:
            delta = abs(v[prns[1]] - v[prns[0]])
            all_deltas.append(delta)
    return np.mean(all_deltas) if all_deltas else 0.0

# --- MAIN EXECUTION ---
prefix = "vortex_full_manifold_audit_2000_2022_"
sys.stdout = Logger(f"{prefix}results.txt")

print("="*85)
print("VORTEX-HUNT FORENSIC AUDIT: DATA DISCOVERY MODE")
print("SEARCHING: [Local Directory] AND [../Data/ subfolders]")
print("="*85)

weeks = {
    "2000": "1060", "2002": "1160", "2003": "1210", "2004": "1263", 
    "2005": "1320", "2006": "1377", "2007": "1433", "2008": "1500", 
    "2009": "1559", "2010": "1590", "2011": "1642", "2012": "1686",
    "2013": "1738", "2014": "1790", "2015": "1843", "2016": "1895",
    "2018": "1999", "2020": "2103", "2022": "2208"
}

years_list = sorted(weeks.keys(), key=int)
cod_vals, igs_vals, iad_ratios = [], [], []

print(f"{'YEAR':<6} | {'PRN PAIR':<14} | {'COD σ²':<12} | {'IGS σ²':<12} | {'IAD RATIO'}")
print("-" * 85)

for year in years_list:
    week = weeks[year]
    y_int = int(year)
    prns = ['G01', 'G25'] if y_int < 2009 else ['G03', 'G25']

    cod_files = find_files(f"cod{week}*.clk")
    igs_files = find_files(f"igs{week}*.clk")
    if y_int == 2000 and not igs_files:
        igs_files = find_files(f"jpl{week}*.clk")

    v_cod = run_audit(f"COD_{year}", cod_files, prns)
    v_igs = run_audit(f"IGS_{year}", igs_files, prns)
    
    iad = v_igs / v_cod if v_cod > 0 else 0
    cod_vals.append(v_cod)
    igs_vals.append(v_igs)
    iad_ratios.append(iad)
    
    print(f"{year:<6} | {str(prns):<14} | {v_cod:<12.2e} | {v_igs:<12.2e} | {iad:>8.2f}x")

# --- 1. THE TOPOLOGICAL LADDER GRAPH (RESTORED) ---
plt.figure(figsize=(14, 8), dpi=150)
plt.yscale('log')

plt.plot(years_list, cod_vals, 'o-', label='COD (Mathematical Ground State)', color='#0047AB', linewidth=2)
plt.plot(years_list, igs_vals, 's--', label='IGS/JPL (Observed Consensus)', color='#D7191C', alpha=0.8)

plt.axvspan('2000', '2002', color='green', alpha=0.05, label='Control Baseline')
plt.axvspan('2003', '2004', color='yellow', alpha=0.1, label='Initial Fracture')
plt.axvspan('2008', '2010', color='red', alpha=0.15, label='2008 Rupture')
plt.axvspan('2013', '2016', color='purple', alpha=0.1, label='Phase Snap')

plt.title('Forensic Manifold Audit: 2000-2022 Clock Divergence', fontsize=14)
plt.xlabel('Forensic Year', fontsize=12)
plt.ylabel('Jerk Variance [ns$^2$] (Log Scale)', fontsize=12)
plt.xticks(rotation=45)
plt.legend(loc='upper left', frameon=True, shadow=True, fontsize='small')
plt.grid(True, which="both", ls="-", alpha=0.1)

plt.savefig(f"{prefix}master_graph.png", dpi=300)

# --- 2. ZOOMED M-SHAPE ANALYSIS (RESTORED) ---
plt.figure(figsize=(10, 6))
zoom_years = [y for y in years_list if int(y) >= 2011]
zoom_iad = [iad_ratios[years_list.index(y)] for y in zoom_years]

plt.plot(zoom_years, zoom_iad, 'o-', color='purple', linewidth=2, label='IAD Ratio')
plt.axhline(y=10, color='gray', linestyle='--', alpha=0.5, label='Tension Threshold')
plt.title('Zoomed Forensic Audit: 2011-2022 Oscillation')
plt.ylabel('Inter-Agency Divergence (IAD) Ratio')
plt.grid(True, alpha=0.3)
plt.legend()

plt.savefig(f"{prefix}M_SHAPE_ZOOM.png")

# --- FINAL CSV EXPORT ---
export_rows = []
for year in years_list:
    week = weeks[year]
    files = find_files(f"igs{week}*.clk")
    if int(year) == 2000 and not files:
        files = find_files(f"jpl{week}*.clk")

    for f_path in files:
        offsets = []
        with open(f_path, 'r', errors='ignore') as f:
            for line in f:
                if 'AS ' in line and 'G25' in line:
                    parts = line.split()
                    try:
                        val = float(parts[-1]) * 1e9 
                        offsets.append(val)
                    except: continue
        
        if len(offsets) > 10:
            residuals = np.diff(offsets, n=2)
            for r in residuals:
                export_rows.append({'TIMESTAMP': f"{year}_DATA", 'SOURCE': os.path.basename(f_path), 'X': r})

if export_rows:
    pd.DataFrame(export_rows).to_csv("G25_Full_Timeline_Audit.csv", index=False)
    print("\nSUCCESS: Data exported to G25_Full_Timeline_Audit.csv")

sys.stdout.log.close()
sys.stdout = sys.stdout.terminal
# %%