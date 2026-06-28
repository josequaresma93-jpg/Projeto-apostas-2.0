
from datetime import date
import pandas as pd
import streamlit as st
from core.database import get_leagues, get_teams, add_bet
from core.team_strength import estimate_lambdas, explain_context
from core.markets import calc_markets
from core.value import compare_odds, context_confidence
from services.seed import seed_sample_data

st.title("🔍 Scanner de Valor Explicável")
leagues = get_leagues()
league_options = ["Série B"] + [x for x in leagues["name"].tolist() if x != "Série B"]
league = st.selectbox("Liga", league_options)
teams = get_teams(league)["name"].tolist()
if not teams:
    st.warning("Nenhum time cadastrado.")
    if st.button("Carregar dados de exemplo"):
        seed_sample_data()
        st.rerun()
    teams = ["Vila Nova", "Novorizontino"]

c1,c2,c3,c4 = st.columns(4)
home = c1.selectbox("Mandante", teams, index=0)
away = c2.selectbox("Visitante", teams, index=min(1, len(teams)-1))
bankroll = c3.number_input("Banca R$", 100.0, 1000000.0, 1000.0, 100.0)
min_edge = c4.number_input("Edge mínimo", 0.0, 0.50, 0.06, 0.01)

a1,a2,a3 = st.columns(3)
adj_home = a1.number_input("Ajuste mandante em gols", -1.0, 1.0, 0.0, 0.05)
adj_away = a2.number_input("Ajuste visitante em gols", -1.0, 1.0, 0.0, 0.05)
manual_conf = a3.slider("Confiança manual", 0, 100, 75)

lh, la, hs, aw, warning = estimate_lambdas(home, away, league, adj_home, adj_away)
if warning:
    st.warning(warning)
confidence = context_confidence(hs, aw, manual_conf)
explanation = explain_context(hs, aw, lh, la)

m1,m2,m3,m4,m5,m6 = st.columns(6)
m1.metric("Lambda Casa", f"{lh:.2f}")
m2.metric("Lambda Fora", f"{la:.2f}")
m3.metric("Casa BTTS", f"{hs['btts']:.0%}")
m4.metric("Fora BTTS", f"{aw['btts']:.0%}")
m5.metric("Confiança", f"{confidence:.0f}/100")
m6.metric("Forma média", f"{(hs['form']+aw['form'])/2:.0f}")

with st.expander("Por que o modelo chegou nisso?"):
    st.write(explanation)

markets = calc_markets(lh, la)
main_markets = ["BTTS Sim","BTTS Não","Over 1.5","Under 2.5","Over 2.5","Under 3.5","Casa ML","Empate","Fora ML","Casa DNB","Fora DNB","Casa AH -0.5","Casa AH +0","Fora AH +0.5","Fora AH +0"]
rows = []
cols = st.columns(5)
for i, market in enumerate(main_markets):
    with cols[i % 5]:
        odd = st.number_input(market, 0.0, 50.0, 0.0, 0.01, key=f"odd_{market}")
        if odd > 0:
            rows.append({"bookmaker":"Manual", "market":market, "odd":odd})

odds_df = pd.DataFrame(rows, columns=["bookmaker","market","odd"])
radar = compare_odds(markets, odds_df, min_edge, bankroll, confidence, explanation)

st.subheader("Radar de Valor")
if radar.empty:
    st.info("Digite pelo menos uma odd acima de 0.")
else:
    st.dataframe(radar[["bookmaker","market","prob","fair_odd","odd","edge","ev","kelly","stake","confidence","grade","decision"]].style.format({
        "prob":"{:.2%}", "fair_odd":"{:.2f}", "odd":"{:.2f}", "edge":"{:.2%}", "ev":"{:.2%}", "kelly":"{:.2%}", "stake":"R$ {:.2f}", "confidence":"{:.0f}"
    }), use_container_width=True)

    labels = [f'{r.bookmaker} | {r.market} | odd {r.odd}' for _, r in radar.iterrows()]
    selected = st.selectbox("Entrada", labels)
    row = radar.iloc[labels.index(selected)]
    stake = st.number_input("Stake R$", 1.0, 100000.0, float(max(1, round(row.stake, 2))), 1.0)
    note = st.text_input("Observação", "")
    if st.button("Salvar no histórico"):
        add_bet(str(date.today()), league, f"{home} x {away}", row.market, row.bookmaker, float(row.odd), float(row.fair_odd), float(row.prob), float(row.edge), float(row.ev), float(row.kelly), float(stake), float(row.confidence), row.grade, row.explanation, note)
        st.success("Aposta salva.")
with st.expander("Todas as probabilidades"):
    st.dataframe(markets.style.format({"prob":"{:.2%}", "fair_odd":"{:.2f}"}), use_container_width=True)
