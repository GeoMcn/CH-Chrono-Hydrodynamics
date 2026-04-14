# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import lombscargle
import pathlib
import os
import re

# --- 1. SETTINGS ---
CENTER_FREQ = 508.6
PREDICTED_SIDEBAND = 491.1
OUTPUT_DIR = "Vortex_Results_2000_Plus"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_target_files():
    """
    Finds moon.* and apollo11_*.npt files.
    Logic: Checks current directory, then ../Data/ recursively.
    """
    patterns = ["moon.*", "apollo11_*.npt"]
    found_files = []
    
    # Get current and parent path
    current_dir = pathlib.Path('.').resolve()
    data_dir = current_dir.parent / "Data"
    
    # 1. Search current directory
    for pattern in patterns:
        found_files.extend([str(p) for p in current_dir.glob(pattern)])
    
    # 2. Search ../Data recursively
    if data_dir.exists() and data_dir.is_dir():
        print(f"--> Searching for data in: {data_dir}")
        for pattern in patterns:
            # rglob searches all subdirectories
            found_files.extend([str(p) for p in data_dir.rglob(pattern)])
    else:
        print(f"--> Warning: 'Data' folder not found at {data_dir}")
        
    return list(set(found_files)) # Remove duplicates if they exist

def extract_year_from_filename(filename):
    """Detects year and filters for >= 2000."""
    # Strip path to look only at filename
    fname = os.path.basename(filename)
    yr = None
    if "moon." in fname:
        yy = fname.split('.')[1][:2]
        year_val = int(yy)
        yr = 1900 + year_val if year_val > 50 else 2000 + year_val
    elif "apollo11_" in fname:
        match = re.search(r'apollo11_(\d{4})', fname)
        if match:
            yr = int(match.group(1))
    
    return yr if (yr is not None and yr >= 2000) else None

def run_historical_analysis_modern():
    # Use the new search logic
    all_files = get_target_files()
    
    year_map = {}
    for f in all_files:
        yr = extract_year_from_filename(f)
        if yr:
            if yr not in year_map: year_map[yr] = []
            year_map[yr].append(f)
            
    sorted_years = sorted(year_map.keys())
    summary_data = []
    freqs = np.linspace(450, 550, 20000)

    if not sorted_years:
        print("[!] No matching files found in current directory or ../Data/")
        return

    print(f"--> Analyzing Modern Epoch (2000-2022). Found {len(sorted_years)} years.")

    for yr in sorted_years:
        year_files = sorted(year_map[yr])
        all_amps = []

        for filename in year_files:
            time_data, range_data = [], []
            try:
                with open(filename, 'r') as f:
                    for i, line in enumerate(f):
                        line = line.strip()
                        if len(line) > 40 and not line.startswith("99999"):
                            try:
                                parts = line.split()
                                # Detect if moon. format or apollo format based on filename
                                if "moon." in os.path.basename(filename):
                                    val = float(line[:15]) 
                                else:
                                    val = float(parts[1])
                                
                                if val > 0:
                                    time_data.append(i)
                                    range_data.append(val)
                            except: continue
            except Exception as e:
                continue

            if len(range_data) > 10:
                t = np.array(time_data)
                y = np.array(range_data)
                # Handle polyfit with relative time to prevent floating point issues with indices
                t_rel = t - t[0]
                y_detrended = y - np.polyval(np.polyfit(t_rel, y, 1), t_rel)
                pgram = lombscargle(t_rel, y_detrended, 2 * np.pi * (freqs / 365.25), precenter=True)
                amp = np.sqrt(4 * pgram / len(t))
                all_amps.append(amp)

        if len(all_amps) > 0:
            avg_amp = np.mean(all_amps, axis=0)
            max_idx = np.argmax(avg_amp)
            peak_freq = freqs[max_idx]
            peak_amp = avg_amp[max_idx]
            
            try:
                half_max = peak_amp / 2
                indices_above_half = np.where(avg_amp >= half_max)[0]
                clusters = np.split(indices_above_half, np.where(np.diff(indices_above_half) > 1)[0] + 1)
                target_cluster = [c for c in clusters if max_idx in c][0]
                vti_index = freqs[target_cluster[-1]] - freqs[target_cluster[0]]
                summary_data.append({"Year": yr, "Freq": peak_freq, "VTI": vti_index})
            except: continue

    if summary_data:
        df = pd.DataFrame(summary_data)
        fig, ax1 = plt.subplots(figsize=(14, 7))

        color = '#0047AB' 
        ax1.set_xlabel('Year (Modern Epoch)')
        ax1.set_ylabel('Resonant Frequency (c/y)', color=color, fontsize=12, fontweight='bold')
        ax1.plot(df['Year'], df['Freq'], marker='o', color=color, lw=2.5, label='Resonance Peak', zorder=3)
        ax1.tick_params(axis='y', labelcolor=color)
        
        plt.xticks(df['Year'], rotation=45) 
        ax1.grid(True, linestyle='--', alpha=0.3)

        ax2 = ax1.twinx()
        color = '#D7191C' 
        ax2.set_ylabel('Vacuum Turbulence Index (VTI)', color=color, fontsize=12, fontweight='bold')
        ax2.plot(df['Year'], df['VTI'], marker='s', linestyle=':', color=color, alpha=0.7, lw=2, label='VTI (Vacuum Stress)')
        ax2.tick_params(axis='y', labelcolor=color)

        ax1.axvspan(2007.5, 2010.5, color='red', alpha=0.1, label='The Great Rupture (1266x Node)')
        ax1.axvspan(2012.5, 2013.5, color='purple', alpha=0.1, label='The Phase Snap')

        plt.title('Modern Manifold Transition: 2000 - 2022 Audit', fontsize=14)
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True)

        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "MODERN_TIMELINE_AUDIT.png"), dpi=300)
        
        print("\n" + "="*45)
        print("    MODERN EPOCH SUMMARY (2000-2022)")
        print("="*45)
        print(df.to_string(index=False))
        print("="*45)

if __name__ == "__main__":
    run_historical_analysis_modern()
# %%