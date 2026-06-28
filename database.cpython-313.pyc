
import sqlite3
from pathlib import Path
from datetime import date
import pandas as pd

DB_PATH = Path("data/projeto_apostas_2_pro.db")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_date TEXT,
            league TEXT,
            home_team TEXT,
            away_team TEXT,
            home_goals INTEGER,
            away_goals INTEGER
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bet_date TEXT,
            league TEXT,
            game TEXT,
            market TEXT,
            odd REAL,
            fair_odd REAL,
            prob REAL,
            edge REAL,
            ev REAL,
            kelly REAL,
            stake REAL,
            result TEXT DEFAULT 'pending',
            profit REAL DEFAULT 0
        )
        """)
        c.commit()

def add_match(match_date, league, home_team, away_team, home_goals, away_goals):
    init_db()
    with connect() as c:
        c.execute("""
        INSERT INTO matches
        (match_date, league, home_team, away_team, home_goals, away_goals)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (str(match_date), league, home_team, away_team, int(home_goals), int(away_goals)))
        c.commit()

def get_matches(league=None):
    init_db()
    with connect() as c:
        if league:
            return pd.read_sql_query(
                "SELECT * FROM matches WHERE league=? ORDER BY match_date DESC, id DESC",
                c, params=(league,)
            )
        return pd.read_sql_query("SELECT * FROM matches ORDER BY match_date DESC, id DESC", c)

def get_leagues():
    df = get_matches()
    if df.empty:
        return []
    return sorted(df["league"].dropna().unique().tolist())

def get_teams(league=None):
    df = get_matches(league)
    if df.empty:
        return []
    teams = set(df["home_team"].tolist()) | set(df["away_team"].tolist())
    return sorted(teams)

def last_home(team, league=None, n=10, before_date=None):
    df = get_matches(league)
    if df.empty:
        return df
    df = df[df["home_team"].str.lower() == team.lower()]
    if before_date:
        df = df[df["match_date"] < str(before_date)]
    return df.head(n)

def last_away(team, league=None, n=10, before_date=None):
    df = get_matches(league)
    if df.empty:
        return df
    df = df[df["away_team"].str.lower() == team.lower()]
    if before_date:
        df = df[df["match_date"] < str(before_date)]
    return df.head(n)

def save_bet(league, game, market, odd, fair_odd, prob, edge, ev, kelly_value, stake):
    init_db()
    with connect() as c:
        c.execute("""
        INSERT INTO bets
        (bet_date, league, game, market, odd, fair_odd, prob, edge, ev, kelly, stake)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(date.today()), league, game, market, float(odd), float(fair_odd),
            float(prob), float(edge), float(ev), float(kelly_value), float(stake)
        ))
        c.commit()

def get_bets():
    init_db()
    with connect() as c:
        return pd.read_sql_query("SELECT * FROM bets ORDER BY id DESC", c)

def update_bet_result(bet_id, result):
    init_db()
    with connect() as c:
        row = c.execute("SELECT odd, stake FROM bets WHERE id=?", (int(bet_id),)).fetchone()
        if not row:
            return
        odd, stake = row
        if result == "win":
            profit = stake * (odd - 1)
        elif result == "half_win":
            profit = (stake / 2) * (odd - 1)
        elif result == "push":
            profit = 0
        elif result == "half_loss":
            profit = -stake / 2
        elif result == "loss":
            profit = -stake
        else:
            profit = 0
            result = "pending"
        c.execute("UPDATE bets SET result=?, profit=? WHERE id=?", (result, profit, int(bet_id)))
        c.commit()

def performance_metrics():
    df = get_bets()
    if df.empty:
        return {"bets": 0, "stake": 0, "profit": 0, "roi": 0, "hit_rate": 0}
    settled = df[df["result"].isin(["win", "half_win", "push", "half_loss", "loss"])]
    if settled.empty:
        return {"bets": 0, "stake": 0, "profit": 0, "roi": 0, "hit_rate": 0}
    stake = settled["stake"].sum()
    profit = settled["profit"].sum()
    wins = settled[settled["result"].isin(["win", "half_win"])]
    return {
        "bets": len(settled),
        "stake": stake,
        "profit": profit,
        "roi": profit / stake if stake else 0,
        "hit_rate": len(wins) / len(settled) if len(settled) else 0,
    }

def seed_demo():
    sample = [
        ("2026-06-01","Série B","Vila Nova","Time A",2,1),
        ("2026-05-25","Série B","Vila Nova","Time B",1,0),
        ("2026-05-18","Série B","Vila Nova","Time C",1,1),
        ("2026-05-11","Série B","Vila Nova","Time D",0,0),
        ("2026-05-04","Série B","Vila Nova","Time E",2,0),
        ("2026-04-27","Série B","Vila Nova","Time K",3,1),
        ("2026-04-20","Série B","Vila Nova","Time L",0,1),
        ("2026-04-13","Série B","Vila Nova","Time M",1,1),
        ("2026-04-06","Série B","Vila Nova","Time N",2,2),
        ("2026-03-30","Série B","Vila Nova","Time O",1,0),
        ("2026-06-02","Série B","Time F","Novorizontino",1,1),
        ("2026-05-26","Série B","Time G","Novorizontino",0,2),
        ("2026-05-19","Série B","Time H","Novorizontino",2,1),
        ("2026-05-12","Série B","Time I","Novorizontino",1,0),
        ("2026-05-05","Série B","Time J","Novorizontino",1,1),
        ("2026-04-28","Série B","Time P","Novorizontino",0,0),
        ("2026-04-21","Série B","Time Q","Novorizontino",2,2),
        ("2026-04-14","Série B","Time R","Novorizontino",1,2),
        ("2026-04-07","Série B","Time S","Novorizontino",3,1),
        ("2026-03-31","Série B","Time T","Novorizontino",0,1),
        ("2026-06-01","Série A","Palmeiras","Time Z",2,0),
        ("2026-05-25","Série A","Palmeiras","Time Y",3,1),
        ("2026-05-18","Série A","Time X","Flamengo",1,2),
        ("2026-05-11","Série A","Time W","Flamengo",0,1),
    ]
    for row in sample:
        add_match(*row)
