
import pandas as pd
from core.poisson import score_matrix, fair_odd

def calc_markets(lambda_home, lambda_away):
    df = score_matrix(lambda_home, lambda_away)
    margin = df.home_goals - df.away_goals
    total_goals = df.home_goals + df.away_goals

    p_home = df.loc[margin > 0, "prob"].sum()
    p_draw = df.loc[margin == 0, "prob"].sum()
    p_away = df.loc[margin < 0, "prob"].sum()
    btts = df.loc[(df.home_goals > 0) & (df.away_goals > 0), "prob"].sum()

    markets = [
        {"market": "Casa ML", "prob": p_home},
        {"market": "Empate", "prob": p_draw},
        {"market": "Fora ML", "prob": p_away},
        {"market": "Casa DNB", "prob": p_home + 0.5*p_draw},
        {"market": "Fora DNB", "prob": p_away + 0.5*p_draw},
        {"market": "BTTS Sim", "prob": btts},
        {"market": "BTTS Não", "prob": 1-btts},
    ]

    for line in [0.5,1.5,2.5,3.5,4.5,5.5]:
        over = df.loc[total_goals > line, "prob"].sum()
        markets.append({"market": f"Over {line}", "prob": over})
        markets.append({"market": f"Under {line}", "prob": 1-over})

    for line in [-2.5,-2.0,-1.5,-1.0,-0.5,0,0.5,1.0,1.5,2.0,2.5]:
        wh = df.loc[(margin + line) > 0, "prob"].sum()
        ph = df.loc[(margin + line) == 0, "prob"].sum()
        wa = df.loc[(-margin + line) > 0, "prob"].sum()
        pa = df.loc[(-margin + line) == 0, "prob"].sum()
        markets.append({"market": f"Casa AH {line:+}", "prob": wh + 0.5*ph})
        markets.append({"market": f"Fora AH {line:+}", "prob": wa + 0.5*pa})

    out = pd.DataFrame(markets)
    out["fair_odd"] = out["prob"].apply(fair_odd)
    return out.sort_values("prob", ascending=False).reset_index(drop=True)
