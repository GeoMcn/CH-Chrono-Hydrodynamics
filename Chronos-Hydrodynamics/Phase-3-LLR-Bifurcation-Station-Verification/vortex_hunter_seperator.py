# %%
import pathlib
import os

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

def split_llr_final(input_filename):
    TEXAS = "7080"
    FRANCE = "7845"
    
    # Locate the input file using the new search logic
    target_path = find_file(input_filename)
    
    if not target_path:
        print(f"[!] Error: File '{input_filename}' not found locally or in ../Data/")
        return
    
    file1 = f"station_texas_{TEXAS}.txt"
    file2 = f"station_france_{FRANCE}.txt"
    
    print(f"--> Scanning for IDs in: {target_path}")
    
    try:
        with open(target_path, 'r') as infile, \
             open(file1, 'w') as out_tx, \
             open(file2, 'w') as out_fr:
            
            lines = infile.readlines()
            tx_count = 0
            fr_count = 0
            
            for i in range(len(lines)):
                line = lines[i].strip()
                
                # We only look at the 'Header' line (the one that starts with 0000)
                if line.startswith("0000") and len(line) > 20:
                    # Search for the ID in the first 25 characters of the line
                    header_segment = line[:25]
                    
                    if TEXAS in header_segment:
                        out_tx.write(lines[i])
                        if i + 1 < len(lines): out_tx.write(lines[i+1])
                        tx_count += 1
                    elif FRANCE in header_segment:
                        out_fr.write(lines[i])
                        if i + 1 < len(lines): out_fr.write(lines[i+1])
                        fr_count += 1
            
            print(f"[+] Final Success!")
            print(f"[+] Texas (7080): {tx_count} records")
            print(f"[+] France (7845): {fr_count} records")
            
    except Exception as e:
        print(f"[!] Error processing file: {e}")

# --- RUN IT ---
# The script will now find moon.0912 even if it is tucked away in ../Data/2009/moon.0912
split_llr_final("moon.0912")
# %%