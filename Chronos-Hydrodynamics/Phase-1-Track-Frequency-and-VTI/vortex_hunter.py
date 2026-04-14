# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import lombscargle
import pathlib
import sys

# --- 1. SETTINGS ---
CENTER_FREQ = 508.6
FILENAME = "moon.0811" 
PREDICTED_SIDEBAND = 491.1

def locate_file(filename):
    """
    Search logic: 
    1. Current folder. 
    2. ../Data/ recursively.
    """
    current_path = pathlib.Path(__file__).parent.resolve()
    
    # 1. Check current directory
    local_file = current_path / filename
    if local_file.exists():
        return local_file
    
    # 2. Check ../Data folder recursively
    data_dir = current_path.parent / "Data"
    if data_dir.exists():
        print(f"--> Local file not found. Searching Data directory: {data_dir}")
        # rglob('*') searches all subdirectories
        for path in data_dir.rglob(filename):
            if path.is_file():
                return path
                
    return None

def run_precision_scan():
    target_path = locate_file(FILENAME)
    
    if target_path is None:
        print(f"[!] ERROR: File '{FILENAME}' not found locally or in ../Data/ subfolders.")
        return

    print(f"--> Found File: {target_path}")
    print(f"--> Performing Precision Analysis...")
    
    time_data, range_data = [], []
    
    # Use the resolved target_path to open the file
    with open(target_path, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if len(line) > 50 and not line.startswith("99999"):
                try:
                    val = float(line[:15])
                    if val > 0:
                        time_data.append(i)
                        range_data.append(val)
                except: continue

    if len(range_data) > 5:
        t = np.array(time_data)
        y = np.array(range_data)
        # Handle polyfit with relative time to avoid large number instabilities
        t_norm = t - t[0]
        y_detrended = y - np.polyval(np.polyfit(t_norm, y, 1), t_norm)
        
        # High-resolution frequency scan
        freqs = np.linspace(450, 530, 20000)
        pgram = lombscargle(t_norm, y_detrended, 2 * np.pi * (freqs / 365.25), precenter=True)
        amp = np.sqrt(4 * pgram / len(t))
        
        # --- PEAK DETECTION ---
        max_idx = np.argmax(amp)
        peak_freq = freqs[max_idx]
        peak_amp = amp[max_idx]
        
        # --- TURBULENCE CALCULATION (FWHM) ---
        half_max = peak_amp / 2
        indices_above_half = np.where(amp >= half_max)[0]
        peak_cluster = np.split(indices_above_half, np.where(np.diff(indices_above_half) > 1)[0] + 1)
        target_cluster = [c for c in peak_cluster if max_idx in c][0]
        
        fwhm_width = freqs[target_cluster[-1]] - freqs[target_cluster[0]]
        vti_index = fwhm_width  
        
        print(f"\n[!] DATA SPIKE DETECTED AT: {peak_freq:.2f} c/y")
        print(f"[!] PREDICTED SIDEBAND: {PREDICTED_SIDEBAND} c/y")
        print(f"[!] MARGIN OF ERROR: {abs(peak_freq - PREDICTED_SIDEBAND):.4f}")
        print(f"[!] VACUUM TURBULENCE INDEX (VTI): {vti_index:.4f}")

        # --- PLOTTING ---
        plt.figure(figsize=(14, 7))
        plt.plot(freqs, amp, color='black', lw=1.2, label='LLR Signal')
        plt.hlines(y=half_max, xmin=freqs[target_cluster[0]], xmax=freqs[target_cluster[-1]], 
                   color='orange', lw=4, alpha=0.5, label=f'Turbulence Belt (VTI: {vti_index:.2f})')
        plt.scatter(peak_freq, peak_amp, color='gold', s=100, edgecolors='black', zorder=5, label='Detected Peak')
        plt.axvline(PREDICTED_SIDEBAND, color='blue', ls=':', lw=2, label='Predicted Sideband (491.1)')
        plt.axvline(CENTER_FREQ, color='red', ls='--', alpha=0.3, label='Theoretical Center (508.6)')
        
        plt.title(f"Quantum Vortex Precision Scan: {FILENAME} | VTI: {vti_index:.2f}")
        plt.xlabel("Frequency (Cycles / Year)")
        plt.ylabel("Signal Strength")
        plt.legend()
        plt.grid(alpha=0.15)
        
        # Save figures in the script's current directory
        save_name = FILENAME.replace(".", "_")
        plt.savefig(f"figure_{save_name}.pdf") 
        plt.savefig(f"figure_{save_name}.png", dpi=300)
        plt.show()
    else:
        print("[!] Not enough data points found in file.")

if __name__ == "__main__":
    run_precision_scan()
# %%