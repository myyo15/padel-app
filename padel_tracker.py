{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import matplotlib.pyplot as plt\
import os\
import base64  # Para contrase\'f1a simple (opcional)\
\
PLAYERS = ['Juan', 'Duro', 'Kareka', 'Oscar']\
DATA_FILE = 'padel_data.csv'\
PASSWORD = "padel123"  # Cambia esto a una contrase\'f1a que compart\'e1is los 4\
\
# Funci\'f3n para verificar contrase\'f1a (simple, no ultra-segura)\
def check_password():\
    def password_entered():\
        if st.session_state["password"] == PASSWORD:\
            st.session_state["password_correct"] = True\
        else:\
            st.session_state["password_correct"] = False\
    if "password_correct" not in st.session_state:\
        st.text_input("Contrase\'f1a para acceder:", type="password", on_change=password_entered, key="password")\
        return False\
    elif not st.session_state["password_correct"]:\
        st.text_input("Contrase\'f1a para acceder:", type="password", on_change=password_entered, key="password")\
        st.error("Contrase\'f1a incorrecta.")\
        return False\
    return True\
\
# Cargar datos\
@st.cache_data\
def load_data():\
    if os.path.exists(DATA_FILE):\
        return pd.read_csv(DATA_FILE)\
    else:\
        df = pd.DataFrame(\{'Jugador': PLAYERS, 'Victorias': [0]*4, 'Diferencia_Juegos': [0]*4\})\
        df.to_csv(DATA_FILE, index=False)\
        return df\
\
# Guardar datos\
def save_data(df):\
    df.to_csv(DATA_FILE, index=False)\
\
# A\'f1adir partido\
def add_match(stats):\
    st.subheader("A\'f1adir Nuevo Partido")\
    team1 = st.multiselect("Equipo 1 (elige 2 jugadores)", PLAYERS, max_selections=2)\
    team2 = st.multiselect("Equipo 2 (elige 2 jugadores)", PLAYERS, max_selections=2)\
    \
    all_players = team1 + team2\
    if len(set(all_players)) != 4 or sorted(all_players) != sorted(PLAYERS):\
        st.error("Deben ser exactamente los 4 jugadores \'fanicos, sin repeticiones.")\
        return stats\
    \
    winner = st.radio("Ganador", ["Equipo 1", "Equipo 2"])\
    diff = st.number_input("Diferencia de juegos (positivo)", min_value=1)\
    \
    win_team = team1 if winner == "Equipo 1" else team2\
    lose_team = team2 if winner == "Equipo 1" else team1\
    \
    for player in win_team:\
        stats.loc[stats['Jugador'] == player, 'Victorias'] += 1\
        stats.loc[stats['Jugador'] == player, 'Diferencia_Juegos'] += diff\
    \
    for player in lose_team:\
        stats.loc[stats['Jugador'] == player, 'Diferencia_Juegos'] -= diff\
    \
    st.success("Partido a\'f1adido.")\
    return stats\
\
# Ver stats\
def view_stats(stats):\
    st.subheader("Estad\'edsticas Actuales")\
    stats_sorted = stats.sort_values(by=['Victorias', 'Diferencia_Juegos'], ascending=False)\
    st.dataframe(stats_sorted)\
\
# Ver gr\'e1fico\
def view_graph(stats):\
    st.subheader("Gr\'e1fico de Estad\'edsticas")\
    stats_sorted = stats.sort_values(by=['Victorias', 'Diferencia_Juegos'], ascending=False)\
    fig, ax1 = plt.subplots()\
    \
    ax1.bar(stats_sorted['Jugador'], stats_sorted['Victorias'], color='b', alpha=0.7)\
    ax1.set_ylabel('Victorias', color='b')\
    ax1.tick_params(axis='y', labelcolor='b')\
    \
    ax2 = ax1.twinx()\
    ax2.plot(stats_sorted['Jugador'], stats_sorted['Diferencia_Juegos'], color='r', marker='o')\
    ax2.set_ylabel('Diferencia de Juegos', color='r')\
    ax2.tick_params(axis='y', labelcolor='r')\
    \
    plt.title('Estad\'edsticas de P\'e1del')\
    st.pyplot(fig)\
\
# Main app\
def main():\
    st.title("Tracker de P\'e1del - Los 4 Amigos")\
    if not check_password():\
        st.stop()\
    \
    stats = load_data()\
    \
    menu = st.sidebar.selectbox("Men\'fa", ["A\'f1adir Partido", "Ver Estad\'edsticas", "Ver Gr\'e1fico"])\
    \
    if menu == "A\'f1adir Partido":\
        stats = add_match(stats)\
        save_data(stats)\
    elif menu == "Ver Estad\'edsticas":\
        view_stats(stats)\
    elif menu == "Ver Gr\'e1fico":\
        view_graph(stats)\
\
if __name__ == "__main__":\
    main()}