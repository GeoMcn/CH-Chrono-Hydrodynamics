# %%
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os
import pathlib

def find_target_file(filename):
    """
    Search logic:
    1. Check current script directory.
    2. Go one level up, look for a 'Data' folder, and search recursively.
    """
    # Get the directory where the script is located
    current_dir = pathlib.Path(__file__).parent.resolve()
    
    # 1. Check current directory
    local_path = current_dir / filename
    if local_path.exists():
        print(f"[System] Found file locally: {local_path}")
        return str(local_path)
    
    # 2. Check ../Data folder recursively
    data_dir = current_dir.parent / "Data"
    if data_dir.exists():
        print(f"[System] Local file not found. Searching Data directory: {data_dir}")
        # rglob('*') searches all subdirectories recursively
        for path in data_dir.rglob(filename):
            if path.is_file():
                print(f"[System] Found file in Data tree: {path}")
                return str(path)
                
    return None

def audit_hourly_jitter_fixed(filename, target_prn="G25"):
    """
    Scans high-resolution GPS clock files, calculates quantized jitter levels,
    saves results to a text file, and generates a 'Staircase' graph.
    """
    # --- FILE SEARCH LOGIC ---
    file_path = find_target_file(filename)
    
    if file_path is None:
        print(f"ERROR: File '{filename}' not found locally or in '../Data/' subfolders.")
        return

    # Prefix for outputs
    prefix = f"audit_{target_prn}_"
    
    # Dictionary to store biases by hour
    hourly_data = {i: [] for i in range(24)}
    results_for_export = []
    
    print(f"--- Scanning {file_path} for {target_prn} Temporal Spikes ---")
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('AS') and target_prn in line:
                parts = line.split()
                try:
                    hour = int(parts[5]) 
                    bias = float(parts[8])
                    hourly_data[hour].append(bias)
                except (ValueError, IndexError):
                    continue

    # Setup for Table output and Export
    header = f"{'Hour (UTC)':<12} | {'Jitter (ps)':<20} | {'Status'}"
    separator = "-" * 60
    print(f"\n{header}\n{separator}")
    results_for_export.append(header)
    results_for_export.append(separator)
    
    # CH-Framework Baseline
    baseline_jitter = 128019057854.90 
    hours_list = []
    jitters_list = []

    for hour in range(24):
        biases = hourly_data[hour]
        if len(biases) < 10: 
            continue
        
        y = np.array(biases)
        x = np.arange(len(y))
        slope, intercept, _, _, _ = stats.linregress(x, y)
        jitter = np.std(y - (slope * x + intercept)) * 1e12
        
        diff = abs(jitter - baseline_jitter)
        status = "PHASE SLIP!" if diff > 1000 else "LOCKED"
        
        row = f"{hour:02d}:00 UTC    | {jitter:,.2f} | {status}"
        print(row)
        results_for_export.append(row)
        
        hours_list.append(hour)
        jitters_list.append(jitter)

    # 1. Save results to TXT file
    output_txt = f"{prefix}results.txt"
    with open(output_txt, "w") as f:
        f.write("\n".join(results_for_export))
    print(f"\n[System] Results saved to: {output_txt}")

    # 2. Generate and Save Graph
    if hours_list:
        plt.figure(figsize=(12, 7))
        plt.step(hours_list, jitters_list, where='post', color='#1f77b4', linewidth=2.5, label='Measured Jitter')
        plt.scatter(hours_list, jitters_list, color='red', s=40, zorder=3, label='Hourly Data Nodes')
        
        levels = {
            "Level 0 (Ground)": 127997238777.96,
            "Level 1 (+88M)": 128085110418.43,
            "Level 2 (+175M)": 128172669735.76,
            "Level 3 (Peak Snap)": 128346807669.91
        }
        
        for label, val in levels.items():
            plt.axhline(y=val, color='gray', linestyle='--', alpha=0.3)
            plt.text(max(hours_list)+0.2, val, label, va='center', fontsize=9, color='blue')

        plt.xlabel('Hour (UTC)', fontsize=12)
        plt.ylabel('Vacuum Jitter Magnitude (ps)', fontsize=12)
        plt.title(f'Quantized Phase-Slip Staircase: {target_prn} Vacuum Resonance', fontsize=14)
        plt.xticks(range(0, 25, 2))
        plt.grid(True, which='both', linestyle=':', alpha=0.5)
        plt.legend(loc='upper left')
        plt.tight_layout()
        
        output_png = f"{prefix}graph.png"
        plt.savefig(output_png, dpi=300)
        print(f"[System] Graph saved to: {output_png}")
        plt.show() 
    else:
        print("\n[Warning] No valid data points found to plot.")

# --- EXECUTION ---
# Pass just the filename; the find_target_file function will do the rest.
audit_hourly_jitter_fixed("cod15594.clk_05s")
# %%