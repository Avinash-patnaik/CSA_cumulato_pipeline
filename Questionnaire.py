import os
import pandas as pd
from datetime import datetime
import sys
import csv # Import csv for the quoting option

# File paths
input_folder = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\data\questionnaire\FOLCAPI\bimestre 12"
output_folder = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\data\cumulative output\FOLCAPI"

# --- Create output folder if it doesn't exist ---
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created output folder: {output_folder}")

date_str = datetime.today().strftime("%Y%m%d")

# Output filename
output_filename = f"CUMULATO_DATIRFL_BIMESTRE12_{date_str}.csv"
output_filepath = os.path.join(output_folder, output_filename)

# List all CSV files
try:
    file_list = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.csv')]
    total_files = len(file_list)
    
    if total_files == 0:
        print(f"Error: No .csv files found in {input_folder}")
        sys.exit()
        
    print(f"Found {total_files} CSV files to process.")

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
    # Fixed indentation
    percent = iteration / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {percent*100:6.2f}% ({iteration}/{total})')
    sys.stdout.flush()

# Read & concatenate CSVs as strings to preserve original formatting
print("Starting to read and process files...")
for i, f in enumerate(file_list, start=1):
    try:
        # Your read_csv command is correct, using dtype=str preserves all data
        df = pd.read_csv(f, sep="|", encoding="latin-1", dtype=str, on_bad_lines="skip")
        df_list.append(df)
    except Exception as e:
        print(f"\nWarning: Could not read file {f}. Error: {e}. Skipping this file.")
        
    progress_bar(i, total_files)

# Move to next line after progress bar
print("\nFile reading complete.")

if not df_list:
    print("No data was loaded (all files might have been skipped or empty). Exiting.")
    sys.exit()

# Concatenate all DataFrames
print("Concatenating all data...")
combined = pd.concat(df_list, ignore_index=True)
print("Concatenation complete.")

# Drop duplicates (ID)
try:
    id_col = combined.columns[0]
    print(f"Dropping duplicates based on first column: '{id_col}'...")
    original_rows = len(combined)
    combined = combined.drop_duplicates(subset=[id_col])
    new_rows = len(combined)
    print(f"Dropped {original_rows - new_rows} duplicate rows.")
except IndexError:
    print("Error: DataFrame appears to be empty, cannot get column for dropping duplicates. Skipping drop.")

# Save cumulative file (all as strings, same separator)
print(f"Saving cumulative file to {output_filepath}...")
try:
    # Using quoting=csv.QUOTE_ALL (which is what quoting=1 means)
    # This wraps every single field in quotes, which is great for data integrity.
    combined.to_csv(output_filepath, index=False, sep="|", encoding="latin-1", quoting=csv.QUOTE_ALL)
    print(f"\n✅ ID cumulative file created at: {output_filepath}")
except Exception as e:
    print(f"\nError saving file: {e}")
