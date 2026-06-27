
import streamlit as st
from core.database import add_league, add_team, get_leagues, get_teams
from services.api_placeholders import football_api_status, odds_api_status

st.title("⚙️ Configurações")

with st.form("cadastros"):
    league = st.text_input("Liga", "Série B")
    country = st.text_input("País", "Brasil")
    team = st.text_input("Time", "Vila Nova")
    if st.form_submit_button("Cadastrar"):
        add_league(league, country)
        add_team(team, league)
        st.success("Cadastro salvo.")

c1,c2 = st.columns(2)
c1.subheader("Ligas")
c1.dataframe(get_leagues(), use_container_width=True)
c2.subheader("Times")
c2.dataframe(get_teams(), use_container_width=True)

st.subheader("Integrações futuras")
st.write(football_api_status())
st.write(odds_api_status())
