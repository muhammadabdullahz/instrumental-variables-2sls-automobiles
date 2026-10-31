import pandas as pd

from src.estimate import run_all

res = run_all(pd.read_csv("data/processed/blp.csv"))
res.to_csv("outputs/results.csv")
print(res.round(3).to_string())
