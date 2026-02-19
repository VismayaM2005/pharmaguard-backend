import pandas as pd
import os

DATA_FOLDER = "data"

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".xlsx"):
        excel_path = os.path.join(DATA_FOLDER, file)
        csv_name = file.replace(".xlsx", ".csv")
        csv_path = os.path.join(DATA_FOLDER, csv_name)

        df = pd.read_excel(excel_path)
        df.to_csv(csv_path, index=False)

        print(f"Converted: {file} → {csv_name}")

print("All files converted.")