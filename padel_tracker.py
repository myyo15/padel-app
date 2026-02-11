import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64  # Para contraseña simple (opcional)

PLAYERS = ['Juan', 'Duro', 'Kareka', 'Oscar']
DATA_FILE = 'padel_data.csv'
PASSWORD = "padel123"  # Cambia esto a una contraseña que compartáis los 4

# Función para verificar contraseña (simple, no ultra-segura)
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

# Cargar datos
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame({'Jugador': PLAYERS, 'Victorias': [0]*4, 'Diferencia_Juegos': [0]*4})
        df.to_csv(DATA_FILE, index=False)
        return df

# Guardar datos
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Añadir partido
def add_match(stats):
    st.subheader("Añadir Nuevo Partido")
    team1 = st.multiselect("Equipo 1 (elige 2 jugadores)", PLAYERS, max_selections=2)
    team2 = st.multiselect("Equipo 2 (elige 2 jugadores)", PLAYERS, max_selections=2)
    
    all_players = team1 + team2
    if len(set(all_players)) != 4 or sorted(all_players) != sorted(PLAYERS):
        st.error("Deben ser exactamente los 4 jugadores únicos, sin repeticiones.")
        return stats
    
    winner = st.radio("Ganador", ["Equipo 1", "Equipo 2"])
    diff = st.number_input("Diferencia de juegos (positivo)", min_value=1)
    
    win_team = team1 if winner == "Equipo 1" else team2
    lose_team = team2 if winner == "Equipo 1" else team1
    
    for player in win_team:
        stats.loc[stats['Jugador'] == player, 'Victorias'] += 1
        stats.loc[stats['Jugador'] == player, 'Diferencia_Juegos'] += diff
    
    for player in lose_team:
        stats.loc[stats['Jugador'] == player, 'Diferencia_Juegos'] -= diff
    
    st.success("Partido añadido.")
    return stats

# Ver stats
def view_stats(stats):
    st.subheader("Estadísticas Actuales")
    stats_sorted = stats.sort_values(by=['Victorias', 'Diferencia_Juegos'], ascending=False)
    st.dataframe(stats_sorted)

# Ver gráfico
def view_graph(stats):
    st.subheader("Gráfico de Estadísticas")
    stats_sorted = stats.sort_values(by=['Victorias', 'Diferencia_Juegos'], ascending=False)
    fig, ax1 = plt.subplots()
    
    ax1.bar(stats_sorted['Jugador'], stats_sorted['Victorias'], color='b', alpha=0.7)
    ax1.set_ylabel('Victorias', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    
    ax2 = ax1.twinx()
    ax2.plot(stats_sorted['Jugador'], stats_sorted['Diferencia_Juegos'], color='r', marker='o')
    ax2.set_ylabel('Diferencia de Juegos', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    
    plt.title('Estadísticas de Pádel')
    st.pyplot(fig)

# Main app
def main():
    st.title("Tracker de Pádel - Los 4 Amigos")
    if not check_password():
        st.stop()
    
    stats = load_data()
    
    menu = st.sidebar.selectbox("Menú", ["Añadir Partido", "Ver Estadísticas", "Ver Gráfico"])
    
    if menu == "Añadir Partido":
        stats = add_match(stats)
        save_data(stats)
    elif menu == "Ver Estadísticas":
        view_stats(stats)
    elif menu == "Ver Gráfico":
        view_graph(stats)

if __name__ == "__main__":
    main()
