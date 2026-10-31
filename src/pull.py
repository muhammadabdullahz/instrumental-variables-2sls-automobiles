"""Load the BLP automobile data (Berry, Levinsohn, Pakes 1995) via pyblp and cache it."""
from pathlib import Path

import pandas as pd
import pyblp

RAW = Path("data/raw") / "blp_products.csv"


def pull_blp() -> pd.DataFrame:
    if not RAW.exists():
        pd.read_csv(pyblp.data.BLP_PRODUCTS_LOCATION).to_csv(RAW, index=False)
    return pd.read_csv(RAW)
