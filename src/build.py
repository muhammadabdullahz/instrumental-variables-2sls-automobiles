"""Construct the logit demand variables."""
import numpy as np
import pandas as pd

CONTROLS = ["hpwt", "air", "mpd", "mpg", "space"]
INSTRUMENTS = [f"demand_instruments{i}" for i in range(8)]


def build_panel(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["outside_share"] = 1 - df.groupby("market_ids")["shares"].transform("sum")
    df["log_share_ratio"] = np.log(df["shares"]) - np.log(df["outside_share"])
    df["firm_share"] = df.groupby(["market_ids", "firm_ids"])["shares"].transform("sum")

    assert (df["outside_share"] > 0).all(), "outside share must be positive"
    assert df[["prices", "shares"] + CONTROLS + INSTRUMENTS].notna().all().all(), "missing values"
    assert df["market_ids"].nunique() == 20, "expected 20 yearly markets"
    return df
