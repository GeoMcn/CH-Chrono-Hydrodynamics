# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import lombscargle, find_peaks
import pathlib
import os

# --- SETTINGS FOR THE DECADAL CONTRAST ---
FILE_A = "moon.0003"  # Laminar Control
FILE_B = "moon.0811"  # Rupture Event
FREQ_START, FREQ_END = 460, 505  # Captures both 473 and 484 peaks
RESOLUTION = 100000

def find_file_recursive(filename):
    """
    Search logic:
    1. Check current directory.
    2. Check ../Data/ folder and all its subdirectories.
    """
    # Get current script path
    current_path = pathlib.Path(__file__).parent.resolve()
    
    # 1. Try local check
    local_file = current_path / filename
    if local_file.exists():
        return str(local_file)
    
    # 2. Try ../Data recursive check
    data_dir = current_path.parent / "Data"
    if data_dir.exists():
        # rglob('*') searches every subfolder inside 'Data'
        for path in data_dir.rglob(filename):
            if path.is_file():
                return str(path)
                
    return None

def get_spectral_data(filename):
    # Use the new search logic
    target_path = find_file_recursive(filename)
    
    if target_path is None:
        print(f"[!] Warning: {filename} not found locally or in ../Data/")
        return None, None, None
    
    print(f"--> Found: {target_path}")
    
    time_data, range_data = [], []
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
    
    if not time_data: return None, None, None

    t = np.array(time_data)
    y = np.array(range_data)
    # Using relative time index to avoid large number instabilities in polyfit
    t_rel = t - t[0]
    y_detrended = y - np.polyval(np.polyfit(t_rel, y, 1), t_rel)
    
    freqs = np.linspace(FREQ_START, FREQ_END, RESOLUTION)
    # Power Spectral Density calculation
    pgram = lombscargle(t_rel, y_detrended, 2 * np.pi * (freqs / 365.25), precenter=True)
    return freqs, pgram, len(t)

if __name__ == "__main__":
    print("Processing Decadal Contrast...")
    
    f_a, p_a, n_a = get_spectral_data(FILE_A)
    f_b, p_b, n_b = get_spectral_data(FILE_B)

    if f_a is not None and f_b is not None:
        plt.figure(figsize=(14, 8))
        
        # Plotting both on a Log Scale for Power
        plt.plot(f_a, p_a, color='royalblue', lw=1.5, label=f'2004 Laminar ({FILE_A})', alpha=0.8)
        plt.plot(f_b, p_b, color='crimson', lw=1.5, label=f'2008 Rupture ({FILE_B})', alpha=0.8)
        
        plt.yscale('log') # The key to seeing the 10^6 difference
        
        plt.title("Figure 5: Forensic Power Collapse & Frequency Migration", fontsize=14, fontweight='bold')
        plt.xlabel("Frequency (Cycles / Year)", fontsize=12)
        plt.ylabel("Power Spectral Density (PSD) - Log Scale", fontsize=12)
        
        # Annotate the Frequency Shift
        max_a = f_a[np.argmax(p_a)]
        max_b = f_b[np.argmax(p_b)]
        plt.annotate(f'Shift: {max_a-max_b:.2f} c/y', xy=(max_b, np.max(p_b)), 
                     xytext=(max_b-10, np.max(p_b)*100),
                     arrowprops=dict(facecolor='black', arrowstyle='->'))

        plt.grid(True, which="both", ls="-", alpha=0.1)
        plt.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig("Laminar_vs_Rupture_Contrast.pdf")
        plt.show()

        # Print Text Audit for Copy-Pasting
        print(f"\n{'FILE':<12} | {'PRIMARY PEAK (c/y)':<20} | {'MAX POWER':<15}")
        print("-" * 55)
        print(f"{FILE_A:<12} | {max_a:<20.4f} | {np.max(p_a):<15.2e}")
        print(f"{FILE_B:<12} | {max_b:<20.4f} | {np.max(p_b):<15.2e}")
        print(f"\nPOWER ATTENUATION FACTOR: {np.max(p_a)/np.max(p_b):.2e}")
    else:
        print("\n[!] Error: Analysis failed. Verify files exist in script folder or ../Data/")
# %%