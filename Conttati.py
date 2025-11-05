import os 
import pandas as pd 
from datetime import datetime
import sys

# file paths 
input_folder = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\data\conttati\FOLCAPI\ottobre2025"
output_folder = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\data\cumulative output\FOLCATI"

# Get today date for the output 
date_str = datetime.today().strftime("%Y%m%d")

# Output file pathname 
output_filename = f"CUMULATO_CONTATTIRFL_OTTOBRE_{date_str}.csv"
output_filepath = os.path.join(output_folder, output_filename)

# Read all CSV files in the folder 
try:
    file_list = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.csv')]
    total_files = len(file_list)

    if total_files == 0:
        print(f"No .csv files found in {input_folder}")
        sys.exit()

except FileNotFoundError:
    print(f"Error: Input folder not found at {input_folder}")
    sys.exit()
except Exception as e:
    print(f"An error occurred while listing files: {e}")
    sys.exit()


df_list = []

# Function to display progress bar
def progress_bar(iteration, total, length=40):
    """Displays a simple progress bar in the console."""
    percent = iteration / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '-' * (length - filled_length)
    # Use \r to return to the start of the line
    sys.stdout.write(f'\rProgress: |{bar}| {percent*100:6.2f}% ({iteration}/{total})')
    sys.stdout.flush()

print(f"Starting to read {total_files} files...")

# Read files with progress bar
for i, f in enumerate(file_list, start=1):
    try:
        # --- KEY CHANGE HERE ---
        # Read all columns as strings (dtype=str) to prevent automatic type conversion
        # (e.g., int to float when NaNs are present).
        df = pd.read_csv(
            f, 
            sep="|", 
            encoding="latin-1", 
            on_bad_lines="skip", 
            low_memory=False, 
            dtype=str  # This preserves all data as text
        )
        df_list.append(df)
    except Exception as e:
        print(f"\nError reading file {f}: {e}")
        # Optionally, you could skip this file and continue:
        # continue 
    
    progress_bar(i, total_files)

# Move to next line after progress bar
print("\nFile reading complete.")

if not df_list:
    print("No dataframes were loaded, exiting.")
    sys.exit()

# Concatenate all DataFrames
print("Concatenating all data...")
df = pd.concat(df_list, ignore_index=True)
print("Concatenation complete.")

# Drop duplicates based on first two columns
try:
    id_col = df.columns[:2].tolist()
    print(f"Dropping duplicates based on columns: {id_col}...")
    original_rows = len(df)
    df = df.drop_duplicates(subset=id_col)
    new_rows = len(df)
    print(f"Dropped {original_rows - new_rows} duplicate rows.")
except IndexError:
    print("Error: Could not find first two columns to drop duplicates. Skipping drop.")

# Save the cumulative file 
print(f"Saving cumulative file to {output_filepath}...")
try:
    df.to_csv(output_filepath, index=False, sep="|", encoding="latin-1")
    print(f"\n✅ Cumulative file created at: {output_filepath}")
except Exception as e:
    print(f"\nError saving file: {e}")

print("\nProcess complete.")