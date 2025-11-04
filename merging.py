import os
import sys

# ------------------------
# Define paths
# ------------------------
input_folder = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\data\conttati\FOLCATI\bimestre1112"
output_file = r"C:\Users\P.Avinash\Desktop\Data science\Cumulato FOL\data\cumulative output\conttati_bimestre1112_cumulato.csv"

# List all CSV files
file_list = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
total_files = len(file_list)

# Open output file in binary write mode
with open(output_file, 'wb') as outfile:
    for i, file in enumerate(file_list, start=1):
        file_path = os.path.join(input_folder, file)
        with open(file_path, 'rb') as infile:
            lines = infile.readlines()
            if i == 1:
                # Write all lines (including header) for the first file
                outfile.writelines(lines)
            else:
                # Skip the first line (header) for other files
                outfile.writelines(lines[1:])
        
        # Show percent complete
        percent = (i / total_files) * 100
        sys.stdout.write(f'\rProgress: {percent:.2f}% ({i}/{total_files} files)')
        sys.stdout.flush()

# Move to next line after completion
print(f"\n✅ Cumulative file created at: {output_file}")
