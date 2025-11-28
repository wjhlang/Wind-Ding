import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

# Load local .env (only works on your computer, not cloud if you deleted .env)
load_dotenv()

st.set_page_config(page_title="Wind-ding", page_icon="🎐")

# --- STYLES ---
st.markdown("""
<style>
    .stApp { text-align: center; }
    .big-title { 
        font-size: 40px !important; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 20px;
    }
    .instruction {
        font-size: 20px;
        text-align: center;
        color: #555;
        margin-bottom: 20px;
    }
    /* Make the geolocation button wide and centered */
    div[data-testid="stBlock"] button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        height: 3em;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_weather_by_coords(lat, lon, key):
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

# --- API KEY SETUP ---
api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")

# --- MAIN PAGE LAYOUT ---

st.markdown('<div class="big-title">這個是風鈴 (This is Wind-ding)</div>', unsafe_allow_html=True)

# If we don't have the API key, stop here.
if not api_key:
    st.error("API Key not found. Please check Streamlit Secrets or your .env file.")
    st.stop()

# We use columns to center the button visually
col1, col2, col3 = st.columns([1, 2, 1])


with col2:
    # This places the button in the middle column
    location = streamlit_geolocation()

if location and location['latitude'] is not None:
    # --- PHASE 2: RESULT ---
    
    lat = location['latitude']
    lon = location['longitude']
    
    # 1. Get Weather
    with st.spinner("Checking the wind..."):
        weather_data = get_weather_by_coords(lat, lon, api_key)
    
    if weather_data:
        wind_speed = weather_data['wind']['speed']
        
        # --- SETTINGS (Hidden in code or Expander) ---
        # You can hardcode this or put it in an expander if you really want to change it
        threshold = 5.0 
        is_windy = wind_speed >= threshold
        
        # --- VISUALS ---
        graph_color = "green" if is_windy else "black"
        ding_color = "red" if is_windy else "grey"
        edge_style = "solid" if is_windy else "dashed"
        
        dot_code = f"""
        digraph G {{
            rankdir=TB;
            bgcolor="transparent";
            
            # THE DIAMOND
            node [shape=diamond, style=filled, fillcolor=white, fontname="Helvetica", width=4, height=1.5];
            Start [label="風有在吹嗎？\\n(Is the wind blowing?)"];
            
            # THE CHIME STRIP (Tall Rectangle)
            node [shape=box, fixedsize=true, width=1.5, height=3.5, fontsize=20, penwidth=3];
            Ding [label="\\n\\n叮\\n鈴\\n|\\n\\n(Ding-)", color="{ding_color}"];
            
            # THE ARROW
            Start -> Ding [label=" YES ", color="{graph_color}", fontcolor="{graph_color}", penwidth=3, style="{edge_style}"];
        }}
        """
        
        st.graphviz_chart(dot_code)
        
        # --- METRICS & SOUND ---
        c1, c2 = st.columns(2)
        c1.metric("Location", weather_data['name'])
        c2.metric("Wind Speed", f"{wind_speed} m/s")
        
        if is_windy:
            st.success("💨 It is windy! The chime rings.")
            
            # Play Sound
            sound_path = "sounds/furin.mp3"
            if os.path.exists(sound_path):
                # We use specific MIME type and autoplay
                st.audio(sound_path, format="audio/mp3", autoplay=True)
            else:
                st.warning(f"Sound file not found at: {sound_path}")
        else:
            st.info("🍂 It is calm. The chime sleeps.")
            
    else:
        st.error("Could not fetch weather data.")

else:
    # --- PHASE 1: LANDING PAGE (User hasn't clicked yet) ---
    st.markdown('<p class="instruction">Sooo, where are you?</p>', unsafe_allow_html=True)