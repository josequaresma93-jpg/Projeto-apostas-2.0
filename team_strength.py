import math
import numpy as np
import pandas as pd

def poisson_pmf(k, lam):
    if lam <= 0: return 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def score_matrix(lambda_home, lambda_away, max_goals=8):
    rows=[]
    for h in range(max_goals+1):
        ph=poisson_pmf(h, lambda_home)
        for a in range(max_goals+1): rows.append({'home_goals':h,'away_goals':a,'prob':ph*poisson_pmf(a,lambda_away)})
    df=pd.DataFrame(rows); s=df.prob.sum()
    if s: df['prob']=df.prob/s
    return df

def fair_odd(prob): return np.nan if prob<=0 else 1/prob
