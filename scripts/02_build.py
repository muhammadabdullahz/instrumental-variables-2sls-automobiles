from src.build import build_panel
from src.pull import pull_blp

df = build_panel(pull_blp())
df.to_csv("data/processed/blp.csv", index=False)
print(df.shape)
