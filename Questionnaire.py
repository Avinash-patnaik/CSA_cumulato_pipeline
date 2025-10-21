import os
import pandas as pd
from datetime import datetime
import sys


# File paths
input_folder = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\data\questionnaire\FOLCATI\aprile2025"
output_folder = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\cumulative output"


date_str = datetime.today().strftime("%Y%m%d")

# Output filename
output_file = os.path.join(output_folder, f"CUMULATO_DATICAPIRFL_{date_str}.csv")

# List all CSV files
file_list = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.csv')]
total_files = len(file_list)

df_list = []

# Function to display progress bar
def progress_bar(iteration, total, length=40):
    percent = iteration / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {percent*100:6.2f}% ({iteration}/{total})')
    sys.stdout.flush()

# Read & concatenate CSVs as strings to preserve original formatting
for i, f in enumerate(file_list, start=1):
    df = pd.read_csv(f, sep="|", encoding="latin-1", dtype=str, on_bad_lines="skip")
    df_list.append(df)
    progress_bar(i, total_files)

# Concatenate all DataFrames
combined = pd.concat(df_list, ignore_index=True)

# Drop duplicates (ID)
id_col = combined.columns[0]
combined = combined.drop_duplicates(subset=[id_col])

# Save cumulative file (all as strings, same separator)
combined.to_csv(output_file, index=False, sep="|", encoding="latin-1", quoting=1)


print(f"\n✅ ID cumulative file created at: {output_file}")
