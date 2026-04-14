# %%
import pandas as pd
import matplotlib.pyplot as plt
import pathlib
import os

# --- SETTINGS ---
PREFIX = "erp_analyzer_"

def find_file(filename):
    """
    Search logic:
    1. Check current script directory.
    2. Go one level up, check 'Data' folder, and search recursively.
    """
    # Get the directory where the script is located
    current_dir = pathlib.Path(__file__).parent.resolve()
    
    # 1. Check current directory
    local_path = current_dir / filename
    if local_path.exists():
        return str(local_path)
    
    # 2. Check ../Data folder recursively
    data_dir = current_dir.parent / "Data"
    if data_dir.exists():
        # rglob('*') searches all subdirectories recursively
        for path in data_dir.rglob(filename):
            if path.is_file():
                return str(path)
                
    return None

def forensic_erp_extract(filename):
    """
    Extracts Length of Day (LOD) jitter from ESA Earth Rotation Parameters.
    Focuses on the post-2000 multiplier standard (10**-7 s/day).
    """
    # Locate file using the new search logic
    file_path = find_file(filename)
    
    if not file_path:
        return pd.DataFrame()
    
    mjd_list, lod_list = [], []
    multiplier = 0.1 
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 5 and parts[0].replace('.','').isdigit():
                    try:
                        mjd = float(parts[0])
                        raw_lod = float(parts[4])
                        lod_micros = raw_lod * multiplier
                        
                        if 51544 < mjd < 61000:
                            mjd_list.append(mjd)
                            lod_list.append(lod_micros)
                    except: continue
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return pd.DataFrame()
    
    return pd.DataFrame({'MJD': mjd_list, 'LOD': lod_list})

# Focused dictionary: 2000 - 2022
files = {
    "2000": "esa10607.erp", "2001": "esa11007.erp", "2002": "esa11607.erp",
    "2003": "esa12107.erp", "2004": "esa12637.erp", "2005": "esa13207.erp",
    "2007": "esa14307.erp", "2008": "esa14827.erp", "2009": "esa15597.erp",
    "2010": "esa15867.erp", "2011": "esa16507.erp", "2012": "esa17007.erp", 
    "2013": "esa17387.erp", "2014": "esa17907.erp", "2015": "esa18437.erp", 
    "2016": "esa18957.erp", "2017": "esa19477.erp", "2018": "esa19997.erp", 
    "2019": "esa20517.erp", "2020": "esa21037.erp", "2021": "esa21567.erp", 
    "2022": "esa22087.erp"
}

results = []
print("--> Searching for ERP files...")
for year, fname in files.items():
    df = forensic_erp_extract(fname)
    if not df.empty:
        results.append((df, year))

# Sort chronologically
results.sort(key=lambda x: int(x[1]))

if results:
    print("="*45)
    print(f"{'Year':<10} | {'LOD Jitter (σ) μs':<20}")
    print("-" * 45)
    
    years_plot = []
    jitter_plot = []

    for df, year in results:
        sig = df['LOD'].std()
        years_plot.append(int(year))
        jitter_plot.append(sig)
        print(f"{year:<10} | {sig:<20.4f}")
    
    print("="*45)

    # --- FORENSIC VISUALIZATION ---
    plt.figure(figsize=(12, 6))
    plt.plot(years_plot, jitter_plot, marker='s', color='darkblue', linestyle='-', linewidth=2, label='ESA LOD Jitter')
    plt.axvspan(2007.5, 2009.5, color='orange', alpha=0.15, label='2008 Rupture Zone')
    
    plt.title("Earth Rotation Jitter (ERP LOD) 2000-2022")
    plt.xlabel("Year")
    plt.ylabel("Jitter Magnitude (σ μs)")
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Save the figure
    output_filename = f"{PREFIX}jitter_plot.png"
    plt.savefig(output_filename, dpi=300)
    print(f"--> Graph saved as: {output_filename}")
    
    plt.show()
else:
    print("No ERP data found. Check script location or 'Data' folder one level up.")
# %%