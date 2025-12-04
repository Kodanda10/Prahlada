import pandas as pd
try:
    df = pd.read_excel('data/raw/LGD/Constituency_Report_2025-11-27_01-47-58.xlsx', header=1, nrows=5)
    print(df.columns.tolist())
except Exception as e:
    print(e)
