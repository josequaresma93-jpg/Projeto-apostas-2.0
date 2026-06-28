
import math
import numpy as np
import pandas as pd
from core.database import last_home, last_away

def poisson_prob(k, lam):
    if lam <= 0:
        return 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def fair_odd(prob):
    return np.nan if prob <= 0 else 1 / prob

def estimate_lambdas(home_team, away_team, league):
    h = last_home(home_team, league, 10)
    a = last_away(away_team, league, 10)

    if h.empty or a.empty:
        return 1.25, 1.05, "Sem dados suficientes. Usando lambdas padrão."

    home_gf = h["home_goals"].mean()
    home_ga = h["away_goals"].mean()
    away_gf = a["away_goals"].mean()
    away_ga = a["home_goals"].mean()

    lambda_home = home_gf * 0.55 + away_ga * 0.45
    lambda_away = away_gf * 0.55 + home_ga * 0.45

    return max(0.1, min(4, lambda_home)), max(0.1, min(4, lambda_away)), ""

def score_matrix(lambda_home, lambda_away, max_goals=8):
    rows = []
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            rows.append({
                "home_goals": h,
                "away_goals": a,
                "prob": poisson_prob(h, lambda_home) * poisson_prob(a, lambda_away)
            })
    df = pd.DataFrame(rows)
    total = df["prob"].sum()
    if total > 0:
        df["prob"] = df["prob"] / total
    return df

def market_probabilities(lambda_home, lambda_away):
    df = score_matrix(lambda_home, lambda_away)
    margin = df["home_goals"] - df["away_goals"]
    total_goals = df["home_goals"] + df["away_goals"]

    p_home = df.loc[margin > 0, "prob"].sum()
    p_draw = df.loc[margin == 0, "prob"].sum()
    p_away = df.loc[margin < 0, "prob"].sum()
    p_btts = df.loc[(df["home_goals"] > 0) & (df["away_goals"] > 0), "prob"].sum()

    rows = [
        {"market": "Casa ML", "prob": p_home},
        {"market": "Empate", "prob": p_draw},
        {"market": "Fora ML", "prob": p_away},
        {"market": "Casa DNB", "prob": p_home + 0.5 * p_draw},
        {"market": "Fora DNB", "prob": p_away + 0.5 * p_draw},
        {"market": "BTTS Sim", "prob": p_btts},
        {"market": "BTTS Não", "prob": 1 - p_btts},
    ]

    for line in [0.5, 1.5, 2.5, 3.5, 4.5]:
        over = df.loc[total_goals > line, "prob"].sum()
        rows.append({"market": f"Over {line}", "prob": over})
        rows.append({"market": f"Under {line}", "prob": 1 - over})

    for line in [-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5]:
        home_win = df.loc[(margin + line) > 0, "prob"].sum()
        home_push = df.loc[(margin + line) == 0, "prob"].sum()
        away_win = df.loc[(-margin + line) > 0, "prob"].sum()
        away_push = df.loc[(-margin + line) == 0, "prob"].sum()

        rows.append({"market": f"Casa AH {line:+}", "prob": home_win + 0.5 * home_push})
        rows.append({"market": f"Fora AH {line:+}", "prob": away_win + 0.5 * away_push})

    out = pd.DataFrame(rows)
    out["fair_odd"] = out["prob"].apply(fair_odd)
    return out.sort_values("prob", ascending=False).reset_index(drop=True)

def kelly_fraction(prob, odd):
    if odd <= 1:
        return 0.0
    b = odd - 1
    q = 1 - prob
    return max(0.0, (b * prob - q) / b)

def compare_with_odds(markets_df, odds_df, bankroll, min_edge):
    if odds_df is None or odds_df.empty:
        return pd.DataFrame()
    if not {"market", "odd"}.issubset(odds_df.columns):
        return pd.DataFrame()

    df = odds_df.merge(markets_df, on="market", how="inner")
    if df.empty:
        return df

    df["edge"] = df["odd"] / df["fair_odd"] - 1
    df["ev"] = df["prob"] * df["odd"] - 1
    df["kelly"] = df.apply(lambda r: kelly_fraction(r["prob"], r["odd"]), axis=1)
    df["stake"] = (df["kelly"] * 0.25 * bankroll).clip(0, bankroll * 0.03)

    def decision(row):
        if row["edge"] >= min_edge and row["ev"] > 0:
            return "🟢 ENTRADA"
        if row["ev"] > 0:
            return "🟡 Valor leve"
        return "🔴 Passar"

    df["decision"] = df.apply(decision, axis=1)
    return df.sort_values("edge", ascending=False).reset_index(drop=True)
