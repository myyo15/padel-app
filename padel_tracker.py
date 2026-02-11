import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date

PLAYERS = ['Juan', 'Duro', 'Kareka', 'Oscar']
DATA_FILE = 'padel_data.csv'
MATCHES_FILE = 'padel_matches.csv'  # Nuevo archivo para historial de partidos
PASSWORD = "padel123"  # Cambia si quieres

# Verificar contraseña
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

# Cargar o crear stats por jugador
@st.cache_data
def load_stats():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame({'Jugador': PLAYERS, 'Victorias': [0]*4, 'Diferencia_Juegos': [0]*4})
        df.to_csv(DATA_FILE, index=False)
        return df

# Cargar o crear historial de partidos
@st.cache_data
def load_matches():
    if os.path.exists(MATCHES_FILE):
        return pd.read_csv(MATCHES_FILE)
    else:
        return pd.DataFrame(columns=['Fecha', 'Equipo1', 'Equipo2', 'Ganador', 'Diferencia'])

# Guardar ambos
def save_all(stats, matches):
    stats.to_csv(DATA_FILE, index=False)
    matches.to_csv(MATCHES_FILE, index=False)

# Añadir partido
def add_match(stats, matches):
    st.subheader("Añadir Nuevo Partido")
    
    match_date = st.date_input("Fecha del partido", value=date.today())
    
    team1 = st.multiselect("Equipo 1 (elige 2 jugadores)", PLAYERS, max_selections=2)
    team2 = st.multiselect("Equipo 2 (elige 2 jugadores)", PLAYERS, max_selections=2)
    
    all_players = team1 + team2
    if len(team1) != 2 or len(team2) != 2 or len(set(all_players)) != 4:
        st.error("Cada equipo debe tener exactamente 2 jugadores diferentes. Total: los 4 únicos.")
        return stats, matches
    
    winner = st.radio("Ganador", ["Equipo 1", "Equipo 2"])
    diff = st.number_input("Diferencia de juegos (positivo)", min_value=1, step=1)
    
    win_team = team1 if winner == "Equipo 1" else team2
    lose_team = team2 if winner == "Equipo 1" else team1
    
    # Actualizar stats
    for player in win_team:
        stats.loc[stats['Jugador'] == player, 'Victorias'] += 1
        stats.loc[stats['Jugador'] == player, 'Diferencia_Juegos'] += diff
    
    for player in lose_team:
        stats.loc[stats['Jugador'] == player, 'Diferencia_Juegos'] -= diff
    
    # Guardar en historial
    new_match = pd.DataFrame({
        'Fecha': [match_date],
        'Equipo1': [", ".join(team1)],
        'Equipo2': [", ".join(team2)],
        'Ganador': [winner],
        'Diferencia': [diff]
    })
    matches = pd.concat([matches, new_match], ignore_index=True)
    
    st.success(f"¡Partido del {match_date} añadido!")
    return stats, matches

# Ver estadísticas por jugador
def view_player_stats(stats):
    st.subheader("Estadísticas por Jugador")
    stats_sorted = stats.sort_values(by=['Victorias', 'Diferencia_Juegos'], ascending=False)
    st.dataframe(stats_sorted.style.format({'Diferencia_Juegos': '{:+d}'}))

# Ver historial de partidos
def view_matches(matches):
    st.subheader("Historial de Partidos")
    if matches.empty:
        st.info("Aún no hay partidos registrados.")
    else:
        st.dataframe(matches.sort_values(by='Fecha', ascending=False))

# Ver gráfico
def view_graph(stats):
    st.subheader("Gráfico de Estadísticas")
    stats_sorted = stats.sort_values(by=['Victorias', 'Diferencia_Juegos'], ascending=False)
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    ax1.bar(stats_sorted['Jugador'], stats_sorted['Victorias'], color='skyblue', alpha=0.8)
    ax1.set_ylabel('Victorias', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    ax2 = ax1.twinx()
    ax2.plot(stats_sorted['Jugador'], stats_sorted['Diferencia_Juegos'], color='darkred', marker='o', linewidth=2)
    ax2.set_ylabel('Diferencia de Juegos', color='darkred')
    ax2.tick_params(axis='y', labelcolor='darkred')
    
    plt.title('Estadísticas de Pádel - Los 4 Amigos')
    st.pyplot(fig)

# Main
def main():
    st.title("Tracker de Pádel - Los 4 Amigos")
    if not check_password():
        st.stop()
    
    stats = load_stats()
    matches = load_matches()
    
    menu = st.sidebar.selectbox("Menú", ["Añadir Partido", "Estadísticas Jugadores", "Historial Partidos", "Gráfico"])
    
    if menu == "Añadir Partido":
        stats, matches = add_match(stats, matches)
        save_all(stats, matches)
    elif menu == "Estadísticas Jugadores":
        view_player_stats(stats)
    elif menu == "Historial Partidos":
        view_matches(matches)
    elif menu == "Gráfico":
        view_graph(stats)

if __name__ == "__main__":
    main()
