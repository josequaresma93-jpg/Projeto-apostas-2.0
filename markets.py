import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path('data/projeto_apostas_v4.db')

def conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with conn() as c:
        c.execute('CREATE TABLE IF NOT EXISTS leagues (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, country TEXT, active INTEGER DEFAULT 1)')
        c.execute('CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, league TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS fixtures (id INTEGER PRIMARY KEY AUTOINCREMENT, fixture_date TEXT, league TEXT, home_team TEXT, away_team TEXT, status TEXT DEFAULT "scheduled")')
        c.execute('''CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT, match_date TEXT, league TEXT, home_team TEXT, away_team TEXT,
            home_goals INTEGER, away_goals INTEGER, xg_home REAL DEFAULT 0, xg_away REAL DEFAULT 0, source TEXT DEFAULT 'manual')''')
        c.execute('''CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bet_date TEXT, league TEXT, game TEXT, market TEXT, bookmaker TEXT,
            odd REAL, fair_odd REAL, prob REAL, edge REAL, ev REAL, kelly REAL, stake REAL, confidence REAL,
            grade TEXT, explanation TEXT, result TEXT DEFAULT 'pending', profit REAL DEFAULT 0, closing_odd REAL, clv REAL, note TEXT)''')
        c.execute('CREATE TABLE IF NOT EXISTS api_settings (id INTEGER PRIMARY KEY AUTOINCREMENT, provider TEXT UNIQUE, api_key TEXT, active INTEGER DEFAULT 0)')
        c.commit()

def add_league(name, country='', active=1):
    init_db()
    with conn() as c:
        c.execute('INSERT OR IGNORE INTO leagues (name,country,active) VALUES (?,?,?)', (name,country,active)); c.commit()

def add_team(name, league=''):
    init_db()
    with conn() as c:
        c.execute('INSERT OR IGNORE INTO teams (name,league) VALUES (?,?)', (name,league)); c.commit()

def add_fixture(fixture_date, league, home_team, away_team, status='scheduled'):
    add_league(league, ''); add_team(home_team, league); add_team(away_team, league)
    with conn() as c:
        c.execute('INSERT INTO fixtures (fixture_date,league,home_team,away_team,status) VALUES (?,?,?,?,?)', (str(fixture_date),league,home_team,away_team,status)); c.commit()

def add_match(match_date, league, home_team, away_team, home_goals, away_goals, xg_home=0, xg_away=0, source='manual'):
    add_league(league, ''); add_team(home_team, league); add_team(away_team, league)
    with conn() as c:
        c.execute('''INSERT INTO matches (match_date,league,home_team,away_team,home_goals,away_goals,xg_home,xg_away,source)
                     VALUES (?,?,?,?,?,?,?,?,?)''', (str(match_date),league,home_team,away_team,int(home_goals),int(away_goals),float(xg_home),float(xg_away),source)); c.commit()

def import_matches_csv(file_obj):
    df = pd.read_csv(file_obj)
    required = {'match_date','league','home_team','away_team','home_goals','away_goals'}
    missing = required - set(df.columns)
    if missing: raise ValueError(f'CSV faltando colunas: {missing}')
    for _, r in df.iterrows(): add_match(r.match_date,r.league,r.home_team,r.away_team,r.home_goals,r.away_goals,r.get('xg_home',0),r.get('xg_away',0),'csv')
    return len(df)

def import_fixtures_csv(file_obj):
    df = pd.read_csv(file_obj)
    required = {'fixture_date','league','home_team','away_team'}
    missing = required - set(df.columns)
    if missing: raise ValueError(f'CSV faltando colunas: {missing}')
    for _, r in df.iterrows(): add_fixture(r.fixture_date,r.league,r.home_team,r.away_team,r.get('status','scheduled'))
    return len(df)

def get_leagues(active_only=False):
    init_db(); q='SELECT * FROM leagues' + (' WHERE active=1' if active_only else '') + ' ORDER BY name'
    return pd.read_sql_query(q, conn())

def get_teams(league=None):
    init_db()
    if league: return pd.read_sql_query('SELECT * FROM teams WHERE league=? ORDER BY name', conn(), params=(league,))
    return pd.read_sql_query('SELECT * FROM teams ORDER BY name', conn())

def get_matches(league=None):
    init_db()
    if league: return pd.read_sql_query('SELECT * FROM matches WHERE league=? ORDER BY match_date DESC,id DESC', conn(), params=(league,))
    return pd.read_sql_query('SELECT * FROM matches ORDER BY match_date DESC,id DESC', conn())

def get_fixtures(league=None):
    init_db()
    if league: return pd.read_sql_query('SELECT * FROM fixtures WHERE league=? ORDER BY fixture_date ASC,id DESC', conn(), params=(league,))
    return pd.read_sql_query('SELECT * FROM fixtures ORDER BY fixture_date ASC,id DESC', conn())

def last_home(team, league=None, n=10, before_date=None):
    q, params = 'SELECT * FROM matches WHERE home_team=?', [team]
    if league: q+=' AND league=?'; params.append(league)
    if before_date: q+=' AND match_date < ?'; params.append(before_date)
    q+=' ORDER BY match_date DESC,id DESC LIMIT ?'; params.append(n)
    return pd.read_sql_query(q, conn(), params=params)

def last_away(team, league=None, n=10, before_date=None):
    q, params = 'SELECT * FROM matches WHERE away_team=?', [team]
    if league: q+=' AND league=?'; params.append(league)
    if before_date: q+=' AND match_date < ?'; params.append(before_date)
    q+=' ORDER BY match_date DESC,id DESC LIMIT ?'; params.append(n)
    return pd.read_sql_query(q, conn(), params=params)

def save_api_setting(provider, api_key, active=0):
    init_db()
    with conn() as c:
        c.execute('INSERT OR REPLACE INTO api_settings (provider,api_key,active) VALUES (?,?,?)', (provider,api_key,active)); c.commit()

def get_api_settings():
    init_db(); return pd.read_sql_query('SELECT * FROM api_settings ORDER BY provider', conn())

def add_bet(bet_date, league, game, market, bookmaker, odd, fair_odd, prob, edge, ev, kelly, stake, confidence, grade, explanation, note=''):
    init_db()
    with conn() as c:
        c.execute('''INSERT INTO bets (bet_date,league,game,market,bookmaker,odd,fair_odd,prob,edge,ev,kelly,stake,confidence,grade,explanation,note)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (str(bet_date),league,game,market,bookmaker,odd,fair_odd,prob,edge,ev,kelly,stake,confidence,grade,explanation,note)); c.commit()

def get_bets():
    init_db(); return pd.read_sql_query('SELECT * FROM bets ORDER BY id DESC', conn())

def update_bet_result(bet_id, result, closing_odd=None):
    with conn() as c:
        row=c.execute('SELECT odd,stake FROM bets WHERE id=?',(int(bet_id),)).fetchone()
        if not row: return
        odd, stake = row
        profit = stake*(odd-1) if result=='win' else (stake/2)*(odd-1) if result=='half_win' else 0 if result=='push' else -stake/2 if result=='half_loss' else -stake if result=='loss' else 0
        if result not in ['win','half_win','push','half_loss','loss']: result='pending'
        clv = odd/closing_odd-1 if closing_odd and closing_odd>0 else None
        c.execute('UPDATE bets SET result=?,profit=?,closing_odd=?,clv=? WHERE id=?',(result,profit,closing_odd,clv,int(bet_id))); c.commit()

def metrics(df):
    settled=df[df['result'].isin(['win','half_win','push','half_loss','loss'])].copy()
    if settled.empty: return {'bets':0,'stake':0,'profit':0,'roi':0,'hit_rate':0,'avg_clv':0}
    stake=settled.stake.sum(); profit=settled.profit.sum(); wins=settled[settled.result.isin(['win','half_win'])]
    return {'bets':len(settled),'stake':stake,'profit':profit,'roi':profit/stake if stake else 0,'hit_rate':len(wins)/len(settled),'avg_clv':settled.clv.dropna().mean() if not settled.clv.dropna().empty else 0}
