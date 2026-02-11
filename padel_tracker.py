import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date, time

PLAYERS = ['Juan', 'Duro', 'Kareka', 'Oscar']
PLACES = ['La Finca', 'Oira', 'Prix', 'Otro']

DATA_FILE = 'padel_data.csv'
MATCHES_FILE = 'padel_matches.csv'
PASSWORD = "padel123"  # Cámbiala si quieres

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

# Cargar stats
@st.cache_data
def load_stats():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame({'Jugador': PLAYERS, 'Victorias': [0]*4, 'Diferencia_Juegos': [0]*4})
        df.to_csv(DATA_FILE, index=False)
        return df

# Cargar historial
@st.cache_data
def load_matches():
    if os.path.exists(MATCHES_FILE):
        return pd.read_csv(MATCHES_FILE)
    else:
        return pd.DataFrame(columns=['Fecha', 'Hora', 'Lugar', 'Equipo1', 'Equipo2', 'Ganador', 'Resultado', 'Dif_Juegos'])

# Guardar todo
def save_all(stats, matches):
    stats.to_csv(DATA_FILE, index=False)
    matches.to_csv(MATCHES_FILE, index=False)

# Calcular diferencia neta a partir del resultado
def calculate_game_diff(result_str):
    if not result_str.strip():
        return 0
    sets = [s.strip() for s in result_str.split(',')]
    diff = 0
    for set_score in sets:
        if '-' not in set_score:
            continue
        try:
            a, b = map(int, set_score.split('-'))
            diff += (a - b)
        except:
            pass
    return diff

# Añadir partido
def add_match(stats, matches):
    st.subheader("Añadir Nuevo Partido")
    
    match_date = st.date_input("Fecha del partido", value=date.today())
    
    match_time = st.time_input("Hora del partido", value=time(19, 0))  # Por defecto 19:00
    
    lugar = st.selectbox("Lugar", PLACES)
    lugar_custom = ""
    if lugar == "Otro":
        lugar_custom = st.text_input("Especifica el lugar", "")
        lugar_final = lugar_custom.strip() if lugar_custom.strip() else "Otro (sin especificar)"
    else:
        lugar_final = lugar
    
    team1 = st.multiselect("Equipo 1 (elige 2 jugadores)", PLAYERS, max_selections=2, key="team1_add")
    team2 = st.multiselect("Equipo 2 (elige 2 jugadores)", PLAYERS, max_selections=2, key="team2_add")
    
    all_players = team1 + team2
    if len(team1) != 2 or len(team2) != 2 or len(set(all_players)) != 4:
        st.error("Cada equipo debe tener exactamente 2 jugadores diferentes. Total: los 4 únicos.")
        return stats, matches
    
    winner = st.radio("Ganador", ["Equipo 1", "Equipo 2"])
    
    st.markdown("**Resultado** (ej: 6-4, 6-3 o 6-2, 7-6, 6-4)")
    result_input = st.text_input("Escribe el resultado completo (separado por comas)", "")
    
    if result_input:
        diff = calculate_game_diff(result_input)
    else:
        diff = st.number_input("Diferencia de juegos neta (positivo para el ganador)", min_value=1, value=5, step=1)
    
    if st.button("Añadir Partido"):
        win_team = team1 if winner == "Equipo 1" else team2
        lose_team = team2 if winner == "Equipo 1" else team1
        
        final_diff = abs(diff) if winner == "Equipo 2" and diff > 0 else diff
        if winner == "Equipo 2":
            final_diff = -final_diff
        
        # Actualizar stats
        for player in win_team:
            stats.loc[stats['Jugador'] == player, 'Victorias'] += 1
            stats.loc[stats['Jugador'] == player, 'Diferencia_Juegos'] += final_diff
        
        for player in lose_team:
            stats.loc[stats['Jugador'] == player, 'Diferencia_Juegos'] -= final_diff
        
        # Guardar en historial
        new_match = pd.DataFrame({
            'Fecha': [match_date],
            'Hora': [match_time.strftime("%H:%M")],
            'Lugar': [lugar_final],
            'Equipo1': [", ".join(team1)],
            'Equipo2': [", ".join(team2)],
            'Ganador': [winner],
            'Resultado': [result_input if result_input else f"Dif: {diff}"],
            'Dif_Juegos': [final_diff]
        })
        matches = pd.concat([matches, new_match], ignore_index=True)
        
        st.success(f"Partido añadido: {match_date} a las {match_time.strftime('%H:%M')} en {lugar_final}")
        return stats, matches
    
    return stats, matches

# Ver stats jugadores
def view_player_stats(stats):
    st.subheader("Estadísticas por Jugador")
    stats_sorted = stats.sort_values(by=['Victorias', 'Diferencia_Juegos'], ascending=False)
    st.dataframe(stats_sorted.style.format({'Diferencia_Juegos': '{:+d}'}))

# Ver historial
def view_matches(matches):
    st.subheader("Historial de Partidos")
    if matches.empty:
        st.info("Aún no hay partidos registrados.")
    else:
        st.dataframe(matches.sort_values(by=['Fecha', 'Hora'], ascending=False))

# Gráfico
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
    plt.title('Estadísticas de Pádel')
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
