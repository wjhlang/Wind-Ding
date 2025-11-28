import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

load_dotenv()

st.set_page_config(page_title="Wind-ding", page_icon="🎐")

# --- CSS ---
st.markdown("""
<style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_weather_by_coords(lat, lon, key):
    """Fetch weather using accurate GPS coordinates"""
    if not key:
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- SIDEBAR ---
api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")

with st.sidebar:
    st.header("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("🔑 API Key", type="password")
    
    st.write("📍 **Location**")

    location = streamlit_geolocation()
    
    threshold = st.slider("💨 Wind Threshold (m/s)", 0.0, 20.0, 5.0)

# --- MAIN APP ---
st.markdown('<p class="big-font">這個是風鈴 (This is Wind-ding)</p>', unsafe_allow_html=True)

if not api_key:
    st.warning("👈 Please enter an API Key to start.")
    st.stop()

# Check if user clicked the location button and gave permission
if location and location['latitude'] is not None:
    lat = location['latitude']
    lon = location['longitude']
    
    # Get Weather
    weather_data = get_weather_by_coords(lat, lon, api_key)
    
    if weather_data:
        wind_speed = weather_data['wind']['speed']
        city_name = weather_data['name']
        
        is_windy = wind_speed >= threshold
        
        # --- DRAW MEME ---
        graph_color = "green" if is_windy else "black"
        ding_color = "red" if is_windy else "grey"
        edge_style = "solid" if is_windy else "dashed"

        dot_code = f"""
        digraph G {{
            rankdir=TB;
            node [shape=box, style=filled, fillcolor=white, fontname="Helvetica"];
            bgcolor="transparent";
            
            Start [label="風有在吹嗎？\\n(Is the wind blowing?)", shape=diamond];
            Ding [label="叮鈴—\\n(Ding-)", fontsize=20, color="{ding_color}", penwidth=3];
            
            Start -> Ding [label=" YES ", color="{graph_color}", fontcolor="{graph_color}", penwidth=3, style="{edge_style}"];
        }}
        """
        st.graphviz_chart(dot_code)
        
        # --- METRICS & AUDIO ---
        col1, col2 = st.columns(2)
        col1.metric("Location", city_name)
        col2.metric("Current Wind", f"{wind_speed} m/s")

        if is_windy:
            st.success(f"💨 It is windy in {city_name}! *DING*")
            if os.path.exists("chime.mp3"):
                st.audio("chime.mp3", format="audio/mp3", autoplay=True)
        else:
            st.info("🍂 It is calm.")
            
    else:
        st.error("❌ Error fetching weather. Check API Key.")

else:
    st.info("👈 Click the **'Get Location'** button in the sidebar to start!")
    st.markdown("_(This will ask your browser for permission)_")