import os 
import pandas as pd 
from datetime import datetime
import sys

# file paths 
input_folder = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\data\conttati\FOLCATI\aprile2025"
output_file = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\cumulative output"

# Get today date for the output 
date_str = datetime.today().strftime("%Y%m%d")

# Output file pathname 
output_file = os.path.join(output_file, f"CUMULATO_CONCAPIRFL_{date_str}.csv")

# Read all CSV files in the folder 
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

# Read files with progress bar
for i, f in enumerate(file_list, start=1):
    df = pd.read_csv(f, sep="|", encoding="latin-1", on_bad_lines="skip", low_memory=False)
    df_list.append(df)
    progress_bar(i, total_files)

# Concatenate all DataFrames
df = pd.concat(df_list, ignore_index=True)

# Drop duplicates based on first two columns
id_col = df.columns[:2].tolist()
df = df.drop_duplicates(subset=id_col)

# Save the cumulative file 
df.to_csv(output_file, index=False, sep="|", encoding="latin-1")

# Move to next line after progress bar
print(f"\n✅ Cumulative file created at: {output_file}")
