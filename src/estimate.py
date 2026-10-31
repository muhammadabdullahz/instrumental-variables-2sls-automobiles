"""OLS, 2SLS and LIML logit demand estimates, with diagnostics and implied marginal costs."""
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS, IVLIML

from src.build import CONTROLS, INSTRUMENTS

SPECS = [  # (label, estimator, instruments, fixed effects)
    ("OLS, no FE",             "ols",  None,            ()),
    ("OLS, firm FE",           "ols",  None,            ("C(firm_ids)",)),
    ("2SLS, 8 instruments",    "iv",   INSTRUMENTS,     ()),
    ("2SLS, same-firm 4",      "iv",   INSTRUMENTS[:4], ()),
    ("2SLS, rival-firm 4",     "iv",   INSTRUMENTS[4:], ()),
    ("LIML, 8 instruments",    "liml", INSTRUMENTS,     ()),
    ("2SLS, year FE, 4",       "iv",   INSTRUMENTS[:4], ("C(market_ids)",)),
    ("2SLS, firm FE, 8",       "iv",   INSTRUMENTS,     ("C(firm_ids)",)),
    ("2SLS, firm+year FE, 4",  "iv",   INSTRUMENTS[:4], ("C(firm_ids)", "C(market_ids)")),
]


def fit_ols(df, fe=()):
    rhs = " + ".join(["prices"] + CONTROLS + list(fe))
    return smf.ols(f"log_share_ratio ~ {rhs}", data=df).fit(cov_type="HC1")


def fit_iv(df, instr, fe=(), estimator=IV2SLS):
    rhs = " + ".join(CONTROLS + list(fe))
    f = f"log_share_ratio ~ 1 + {rhs} + [prices ~ {' + '.join(instr)}]"
    return estimator.from_formula(f, data=df).fit(cov_type="robust")


def summarize(df, label, m, kind):
    a = m.params["prices"]
    lo, hi = m.conf_int().loc["prices"]
    elast = a * df["prices"] * (1 - df["shares"])
    mc = df["prices"] + 1 / (a * (1 - df["firm_share"]))        # Bertrand-Nash implied marginal cost
    row = {"spec": label, "alpha": a, "ci_low": lo, "ci_high": hi,
           "inelastic_pct": 100 * (elast.abs() < 1).mean(),
           "negative_mc_pct": 100 * (mc < 0).mean()}
    if kind in ("iv", "liml"):
        fs = m.first_stage.diagnostics.loc["prices"]
        row.update(partial_r2=fs["partial.rsquared"], first_stage_p=fs["f.pval"])
    if kind == "iv":
        t = m.wooldridge_overid
        row.update(overid_stat=t.stat, overid_df=t.df, overid_p=t.pval)
    return row


def run_all(df) -> pd.DataFrame:
    rows = []
    for label, kind, instr, fe in SPECS:
        m = fit_ols(df, fe) if kind == "ols" else fit_iv(df, instr, fe, IVLIML if kind == "liml" else IV2SLS)
        rows.append(summarize(df, label, m, kind))
    return pd.DataFrame(rows).set_index("spec")
