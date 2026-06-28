
from core.database import last_home, last_away

def _form(df, venue):
    if df.empty: return 50
    pts = []
    for _, r in df.iterrows():
        gf = r.home_goals if venue == "home" else r.away_goals
        ga = r.away_goals if venue == "home" else r.home_goals
        pts.append(3 if gf > ga else 1 if gf == ga else 0)
    return 100 * sum(pts) / (3 * len(pts)) if pts else 50

def home_summary(team, league=None, n=10, before_date=None):
    df = last_home(team, league, n, before_date)
    if df.empty:
        return {"games":0, "gf":0, "ga":0, "btts":0, "over25":0, "form":50, "xg":0, "xga":0}
    return {
        "games": len(df),
        "gf": float(df.home_goals.mean()),
        "ga": float(df.away_goals.mean()),
        "btts": float(((df.home_goals>0)&(df.away_goals>0)).mean()),
        "over25": float(((df.home_goals+df.away_goals)>2.5).mean()),
        "form": _form(df, "home"),
        "xg": float(df.xg_home.mean()) if "xg_home" in df else 0,
        "xga": float(df.xg_away.mean()) if "xg_away" in df else 0,
    }

def away_summary(team, league=None, n=10, before_date=None):
    df = last_away(team, league, n, before_date)
    if df.empty:
        return {"games":0, "gf":0, "ga":0, "btts":0, "over25":0, "form":50, "xg":0, "xga":0}
    return {
        "games": len(df),
        "gf": float(df.away_goals.mean()),
        "ga": float(df.home_goals.mean()),
        "btts": float(((df.home_goals>0)&(df.away_goals>0)).mean()),
        "over25": float(((df.home_goals+df.away_goals)>2.5).mean()),
        "form": _form(df, "away"),
        "xg": float(df.xg_away.mean()) if "xg_away" in df else 0,
        "xga": float(df.xg_home.mean()) if "xg_home" in df else 0,
    }

def estimate_lambdas(home_team, away_team, league=None, adj_home=0, adj_away=0, before_date=None):
    hs = home_summary(home_team, league, 10, before_date)
    aw = away_summary(away_team, league, 10, before_date)
    if hs["games"] == 0 or aw["games"] == 0:
        lh, la = 1.25, 1.05
        warning = "Sem dados suficientes. Usando lambdas padrão."
    else:
        lh = hs["gf"]*0.55 + aw["ga"]*0.45
        la = aw["gf"]*0.55 + hs["ga"]*0.45
        warning = ""
        if hs["xg"] > 0 and aw["xga"] > 0:
            lh = 0.80 * lh + 0.20 * ((hs["xg"] + aw["xga"]) / 2)
        if aw["xg"] > 0 and hs["xga"] > 0:
            la = 0.80 * la + 0.20 * ((aw["xg"] + hs["xga"]) / 2)
    return max(0.10, min(4.00, lh+adj_home)), max(0.10, min(4.00, la+adj_away)), hs, aw, warning

def explain_context(hs, aw, lh, la):
    return (
        f"Mandante em casa: {hs['games']} jogos, GF {hs['gf']:.2f}, GA {hs['ga']:.2f}, "
        f"BTTS {hs['btts']:.0%}, Over2.5 {hs['over25']:.0%}, forma {hs['form']:.0f}/100. "
        f"Visitante fora: {aw['games']} jogos, GF {aw['gf']:.2f}, GA {aw['ga']:.2f}, "
        f"BTTS {aw['btts']:.0%}, Over2.5 {aw['over25']:.0%}, forma {aw['form']:.0f}/100. "
        f"Lambdas finais: casa {lh:.2f}, fora {la:.2f}."
    )
