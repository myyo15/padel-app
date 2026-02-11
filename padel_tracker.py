import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date, time

PLAYERS = ['Juan', 'Duro', 'Kareka', 'Oscar']
PLACES = ['La Finca', 'Oira', 'Prix', 'Otro']

DATA_FILE = 'padel_data.csv'
MATCHES_FILE = 'padel_matches.csv'
PASSWORD = "padel123"  # Cambia si quieres

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.text_input("Contraseña para acceder:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Contraseña para acceder:", type="password", on_change=password_entered, key="password")
        st.error("Contraseña incorrecta.")
        return False
    return True

@st.cache_data
def load_stats():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame({'Jugador': PLAYERS, 'Victorias': [0]*4, 'Dif_Juegos': [0]*4})
        df.to_csv(DATA_FILE, index=False)
        return df
    
    # Asegurar columnas necesarias (compatibilidad con versiones antiguas)
    if 'Dif_Juegos' not in df.columns:
        if 'Diferencia_Juegos' in df.columns:
            df = df.rename(columns={'Diferencia_Juegos': 'Dif_Juegos'})
        elif 'Diferencia' in df.columns:
            df = df.rename(columns={'Diferencia': 'Dif_Juegos'})
        else:
            df['Dif_Juegos'] = 0
    
    if 'Victorias' not in df.columns:
        df['Victorias'] = 0
    
    return df

@st.cache_data
def load_matches():
    if os.path.exists(MATCHES_FILE):
        return pd.read_csv(MATCHES_FILE)
    
    cols = ['Fecha', 'Hora', 'Lugar', 'Equipo1', 'Equipo2', 'Ganador', 'Resultado', 'Dif_Juegos']
    return pd.DataFrame(columns=cols)

def save_all(stats, matches):
    stats.to_csv(DATA_FILE, index=False)
    matches.to_csv(MATCHES_FILE, index=False)

def calculate_game_diff(result_str):
    if not result_str.strip():
        return 0
    sets = [s.strip() for s in result_str.split(',')]
    diff = 0
    for s in sets:
        if '-' not in s:
            continue
        try:
            a, b = map(int, s.split('-'))
            diff += a - b
        except:
            pass
    return diff

def add_match(stats, matches):
    st.subheader("Añadir Partido")
    
    fecha = st.date_input("Fecha", value=date.today())
    hora = st.time_input("Hora", value=time(19, 0))
    lugar = st.selectbox("Lugar", PLACES)
    lugar_final = st.text_input("Especifica si es Otro", "") if lugar == "Otro" else lugar
    
    team1 = st.multiselect("Equipo 1", PLAYERS, max_selections=2, key="team1_add")
    team2 = st.multiselect("Equipo 2", PLAYERS, max_selections=2, key="team2_add")
    
    if len(set(team1 + team2)) != 4 or len(team1) != 2 or len(team2) != 2:
        st.error("Deben ser exactamente 4 jugadores únicos, 2 por equipo.")
        return stats, matches
    
    ganador = st.radio("Ganador", ["Equipo 1", "Equipo 2"])
    
    resultado = st.text_input("Resultado (ej: 6-4,6-3)", "")
    
    if resultado:
