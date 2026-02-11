import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date, time

PLAYERS = ['Juan', 'Duro', 'Kareka', 'Oscar']
PLACES = ['La Finca', 'Oira', 'Prix', 'Otro']

DATA_FILE = 'padel_data_v2.csv'     # ← Cambia a _v2 o cualquier nombre nuevo
MATCHES_FILE = 'padel_matches_v2.csv'  # ← Lo mismo
PASSWORD = "padel123"

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.text_input("Contraseña:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Contraseña:", type="password", on_change=password_entered, key="password")
        st.error("Contraseña incorrecta.")
        return False
    return True

@st.cache_data
def load_stats():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    df = pd.DataFrame({'Jugador': PLAYERS, 'Victorias': [0]*4, 'Dif_Juegos': [0]*4})
    df.to_csv(DATA_FILE, index=False)
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
        if '-' not in s: continue
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
    lugar_final = st.text_input("Otro lugar", "") if lugar == "Otro" else lugar
    
    team1 = st.multiselect("Equipo 1", PLAYERS, max_selections=2, key="t1")
    team2 = st.multiselect("Equipo 2", PLAYERS, max_selections=2, key="t2")
    
    if len(set(team1 + team2)) != 4 or len(team1) != 2 or len(team2) != 2:
        st.error("Equipos inválidos: deben ser 2+2 jugadores únicos.")
        return stats, matches
    
    ganador = st.radio("Ganador", ["Equipo 1", "Equipo 2"])
    
    resultado = st.text_input("Resultado (ej: 6-4,6-3)", "")
    
    if resultado:
        dif = calculate_game_diff(resultado)
    else:
        dif = st.number_input("Diferencia neta (positivo)", min_value=1, value=5)
    
    if st.button("Guardar Partido"):
        win_team = team1 if ganador == "Equipo 1" else team2
        lose_team = team2 if ganador == "Equipo 1" else team1
        
        final_dif = dif if ganador == "Equipo 1" else -dif
        
        for p in win_team:
            stats.loc[stats['Jugador'] == p, 'Victorias'] += 1
            stats.loc[stats['Jugador'] == p, 'Dif_Juegos'] += final_dif
        
        for p in lose_team:
            stats.loc[stats['Jugador'] == p, 'Dif_Juegos'] -= final_dif
        
        new_row = {
            'Fecha': fecha,
            'Hora': hora.strftime("%H:%M"),
            'Lugar': lugar_final,
            'Equipo1': ", ".join(team1),
            'Equipo2': ", ".join(team2),
            'Ganador': ganador,
            'Resultado': resultado or f"Dif {dif}",
            'Dif_Juegos': final_dif
        }
        
        matches = pd.concat([matches, pd.DataFrame([new_row])], ignore_index=True)
        
        st.success("Partido guardado")
        save_all(stats, matches)
        return stats, matches  # Retornar actualizados
    
    return stats, matches

def view_player_stats(stats):
    st.subheader("Estadísticas Jugadores")
    sorted_stats = stats.sort_values(by=['Victorias', 'Dif_Juegos'], ascending=False)
    st.dataframe(sorted_stats.style.format({'Dif_Juegos': '{:+d}'}))

def view_matches(matches):
    st.subheader("Historial de Partidos")
    
    # Depuración mínima (puedes comentarla después)
    # st.write("Columnas actuales:", matches.columns.tolist())
    
    if matches.empty:
        st.info("No hay partidos aún.")
    else:
        sort_cols = [c for c in ['Fecha', 'Hora'] if c in matches.columns]
        if sort_cols:
            df_sorted = matches.sort_values(by=sort_cols, ascending=False)
        else:
            df_sorted = matches
        st.dataframe(df_sorted)

def view_graph(stats):
    st.subheader("Gráfico")
    sorted_stats = stats.sort_values(by=['Victorias', 'Dif_Juegos'], ascending=False)
    fig, ax1 = plt.subplots(figsize=(8,5))
    ax1.bar(sorted_stats['Jugador'], sorted_stats['Victorias'], color='skyblue')
    ax1.set_ylabel('Victorias')
    ax2 = ax1.twinx()
    ax2.plot(sorted_stats['Jugador'], sorted_stats['Dif_Juegos'], 'r-o')
    ax2.set_ylabel('Dif Juegos')
    st.pyplot(fig)

def main():
    st.title("Tracker de Pádel - Los 4 Amigos")
    if not check_password():
        st.stop()
    
    stats = load_stats()
    matches = load_matches()
    
    menu = st.sidebar.selectbox("Menú", ["Añadir Partido", "Estadísticas Jugadores", "Historial Partidos", "Gráfico"])
    
    if menu == "Añadir Partido":
        stats, matches = add_match(stats, matches)
    elif menu == "Estadísticas Jugadores":
        view_player_stats(stats)
    elif menu == "Historial Partidos":
        view_matches(matches)
    elif menu == "Gráfico":
        view_graph(stats)

if __name__ == "__main__":
    main()
