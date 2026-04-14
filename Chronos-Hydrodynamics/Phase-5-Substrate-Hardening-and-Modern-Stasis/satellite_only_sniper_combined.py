# %%
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import pathlib
import os

def find_file(filename):
    """
    Priority Search:
    1. Local directory of the script.
    2. One level up -> 'Data' folder -> recursive subfolders.
    """
    # Get the directory where the script is currently located
    current_dir = pathlib.Path(__file__).parent.resolve()
    
    # 1. Search locally
    local_path = current_dir / filename
    if local_path.exists():
        return str(local_path)
    
    # 2. Search in ../Data/ recursively
    data_dir = current_dir.parent / "Data"
    if data_dir.exists():
        # rglob walks through all subdirectories
        for path in data_dir.rglob(filename):
            if path.is_file():
                return str(path)
                
    return None

def get_jitter_data(filename):
    # Use the new search logic to resolve the path
    resolved_path = find_file(filename)
    
    if resolved_path is None:
        print(f"!!! Warning: {filename} not found locally or in ../Data/ tree.")
        return None, None
    
    raw_entries = []
    try:
        with open(resolved_path, 'r') as f:
            for line in f:
                if line.startswith('AR'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            obj_id = parts[1]
                            val = float(parts[-1])
                            if val != 0:
                                raw_entries.append((obj_id, val))
                        except: continue
    except Exception as e:
        print(f"Error reading {resolved_path}: {e}")
        return None, None
    
    if not raw_entries: return None, None
    ids = [e[0] for e in raw_entries]
    target_id = Counter(ids).most_common(1)[0][0]
    offsets = np.array([e[1] for e in raw_entries if e[0] == target_id])
    jitter = np.abs(np.diff(np.diff(offsets))) # Absolute jitter
    clean_jitter = jitter[jitter < 0.1]
    return clean_jitter, target_id

# --- EXECUTION ---
files = ["cod15004.clk", "cod15304.clk", "cod15592.clk"]
colors = ['crimson', 'orange', 'royalblue']
labels = ['Aug 2008: Rupture', 'May 2009: Cooling', 'Nov 2009: Drag-Lock']

# Create subplots to prevent "Hectic" overlapping
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True, dpi=120)

found_any = False
for i, (file, color, label) in enumerate(zip(files, colors, labels)):
    data, tid = get_jitter_data(file)
    if data is not None:
        found_any = True
        # 1. Plot the RAW data as a light 'ghost' in the background
        axes[i].plot(data, color=color, lw=0.5, alpha=0.15)
        
        # 2. Calculate and plot a Rolling Mean (Trend Line)
        smooth_data = pd.Series(data).rolling(window=50, center=True).mean()
        axes[i].plot(smooth_data, color=color, lw=2, label=f"{label} (Smoothed)")
        
        # 3. Add a Mean horizontal line for the 'State' level
        mean_val = np.mean(data)
        axes[i].axhline(mean_val, color='black', ls='--', lw=1, alpha=0.6)
        axes[i].text(0, mean_val*1.2, f"Mean: {mean_val:.2e}", fontsize=9, fontweight='bold')

        # Formatting each subplot
        axes[i].set_yscale('log')
        axes[i].set_ylim(1e-12, 1e-6)
        axes[i].legend(loc='upper right', frameon=False)
        axes[i].grid(True, which="both", ls="-", alpha=0.05)
        axes[i].set_ylabel("$| \Delta^2 \phi |$ [s]")
    else:
        axes[i].text(0.5, 0.5, f"File Not Found: {file}", ha='center', transform=axes[i].transAxes)

if found_any:
    axes[2].set_xlabel("Sample Index (30s Epochs)")
    plt.suptitle("Figure 4: The Great Substrate Decay (Decadal Transition)", fontsize=16, y=0.95)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig("Substrate_Decay_Clean.png")
    plt.show()
else:
    print("No data found for any files. Execution halted.")
# %%