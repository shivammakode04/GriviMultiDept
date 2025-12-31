import pandas as pd

df = pd.read_csv('core/ai_model/dataset.csv')
print(f'Total rows: {len(df)}')
print(f'\nDepartment distribution:\n{df["label"].value_counts()}')
print(f'\nPriority distribution:\n{df["priority"].value_counts()}')
print(f'\nDataset balance score: {len(df) / len(df["label"].unique()):.2f} samples per department')
