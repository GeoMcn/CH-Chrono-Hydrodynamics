# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
import pathlib
import os
import sys

# --- CONFIGURATION ---
prefix = "PSD_Comparison_6th_Degree_"
target_sats = ['G25', 'G03']
fs = 1/300 

# Define Year-Specific Target Files
targets = {
    "2000": [f"cod1060{i}.clk" for i in range(7)],
    "2009": [f"cod1559{i}.clk" for i in range(7)]
}

# --- DIRECTORY RESOLUTION HELPER ---
def find_files(target_list):
    """
    Priority:
    1. Check local directory.
    2. Check ../Data/ recursively.
    """
    script_dir = pathlib.Path(__file__).parent.resolve()
    data_dir = script_dir.parent / "Data"
    
    unique_files = {}
    
    # 1. Search locally
    for target in target_list:
        local_path = script_dir / target
        if local_path.exists():
            unique_files[target] = local_path

    # 2. Search in ../Data/ recursively (only if not found locally or checking for more)
    if data_dir.exists():
        # rglob handles recursive walking
        for path in data_dir.rglob("*.clk"):
            # Skip high-rate files as per original logic
            if path.name in target_list and not path.name.endswith('_05s'):
                if path.name not in unique_files:
                    unique_files[path.name] = path
                    
    return sorted(list(unique_files.values()))

# --- LOGGING SETUP ---
class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self): pass

report_path = f"{prefix}SideBySide_Audit.txt"
sys.stdout = Logger(report_path)

def analyze_year(year_name, target_list):
    print(f"\n--- INITIATING {year_name} LATTICE AUDIT (6TH-DEGREE) ---")
    
    # Use the new prioritized search
    all_files = find_files(target_list)
    
    if not all_files:
        print(f"!!! ERROR: No {year_name} files found in local dir or ../Data/ !!!")
        return None

    data_dict = {sat: [] for sat in target_sats}
    for file_path in all_files:
        print(f"Reading: {file_path.name} (from {file_path.parent.name})")
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('AS'):
                    for sat in target_sats:
                        if sat in line:
                            try:
                                data_dict[sat].append(float(line.split()[9]))
                            except: continue

    results = {}
    plt.figure(figsize=(10, 6))
    
    for sat, color in zip(target_sats, ['magenta', 'cyan']):
        y = np.array(data_dict[sat])
        if len(y) < 100: 
            print(f"Skipping {sat}: Insufficient data points.")
            continue
        
        x_axis = np.arange(len(y))
        poly_6 = np.polyfit(x_axis, y, 6)
        y_deep = y - np.polyval(poly_6, x_axis)
        
        nper = min(len(y_deep), 256)
        freqs, psd = welch(y_deep, fs=fs, nperseg=nper)
        variance = np.var(y_deep)
        
        results[sat] = variance
        plt.semilogy(freqs, psd, label=f'Sat {sat} | Var: {variance:.2e}', color=color)

    plt.title(f'Deep Forensic Audit: {year_name} Baseline', fontsize=12)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('PSD (ns^2/Hz)')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    graph_name = f"{prefix}Plot_{year_name}.png"
    plt.savefig(graph_name, dpi=300)
    print(f"Saved Forensic Graph: {graph_name}")
    return results

# --- EXECUTE BOTH AUDITS ---
summary = {}
summary["2000"] = analyze_year("2000", targets["2000"])
summary["2009"] = analyze_year("2009", targets["2009"])

# --- PRINT SIDE-BY-SIDE REPORT ---
print("\n" + "="*70)
print(f"{'SATELLITE':<15} | {'2000 VARIANCE (ns^2)':<25} | {'2009 VARIANCE (ns^2)':<25}")
print("-"*70)
for sat in target_sats:
    v2000 = summary["2000"].get(sat, 0) if summary["2000"] else 0
    v2009 = summary["2009"].get(sat, 0) if summary["2009"] else 0
    print(f"{sat:<15} | {v2000:<25.2e} | {v2009:<25.2e}")

print("="*70)
if summary["2000"] and summary["2009"]:
    g25_2000 = summary["2000"].get('G25', 0)
    g25_2009 = summary["2009"].get('G25', 0)
    if g25_2009 > 0:
        rigidity_gain = g25_2000 / g25_2009
        print(f"CH-FORENSIC RESULT: G25 RIGIDITY INCREASE: {rigidity_gain:.2f}x")
    
    g03_2009 = summary["2009"].get('G03', 0)
    if g03_2009 > 0:
        print(f"Final 2009 Phase-Lock Ratio (G25/G03): {g25_2009/g03_2009:.4f}")

print(f"\nFULL REPORT SAVED TO: {report_path}")
sys.stdout = sys.__stdout__
plt.show()
# %%