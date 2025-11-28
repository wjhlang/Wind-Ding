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
    /* 1. Center everything */
    .stApp { text-align: center; }
    
    /* 2. Hide Audio Player */
    .stAudio { display: none; }
    
    /* 3. Button Styling "Ring It" */
    /* This targets the geolocation button specifically */
    div[data-testid="stBlock"] button {
        width: 220px !important;
        height: 60px !important;
        background-color: #ff4b4b !important;
        color: transparent !important; /* Hide default icon */
        border-radius: 30px !important;
        border: none !important;
        margin: 20px auto !important;
        display: block !important;
        position: relative;
    }
    
    /* Overlay our own text on the button */
    div[data-testid="stBlock"] button::after {
        content: "🎐 Ring It";
        color: white;
        font-size: 20px;
        font-weight: bold;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
    }

    /* 4. Center the "Try Again" button */
    .stButton button {
        margin: 0 auto;
        display: block;
    }

    /* Title Styling */
    .big-title { 
        font-size: 32px !important; 
        font-weight: bold; 
        font-family: sans-serif;
        margin-bottom: 5px;
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

if not api_key:
    st.error("⚠️ API Key missing. Please ask the administrator 'You know Who'.")
    st.stop()

# Initialize Session State
if 'coords' not in st.session_state:
    st.session_state['coords'] = None

# --- MAIN APP ---

st.markdown('<div class="big-title">這個是風鈴 (This is Wind-ding)</div>', unsafe_allow_html=True)

# PHASE 1: GET LOCATION (Only show if we don't have coords yet)
if st.session_state['coords'] is None:
    st.write("Click below to check the wind.")
    
    # This renders the button. CSS above transforms it into "Ring It"
    location = streamlit_geolocation()
    
    if location and location['latitude'] is not None:
        # Save coords and rerun to enter Phase 2
        st.session_state['coords'] = {'lat': location['latitude'], 'lon': location['longitude']}
        st.rerun()

# PHASE 2: SHOW RESULT (We have coords)
else:
    lat = st.session_state['coords']['lat']
    lon = st.session_state['coords']['lon']
    
    with st.spinner("Listening to the wind..."):
        data = get_weather_by_coords(lat, lon, api_key)

    if data:
        wind_speed_ms = data['wind']['speed']
        wind_speed_kmh = round(wind_speed_ms * 3.6, 1) # Convert for readability
        city_name = data['name']
        
        # LOGIC
        threshold = 5.0 
        is_windy = wind_speed_ms >= threshold
        
        # --- DISPLAY ---
        
        # 1. Metrics
        c1, c2 = st.columns(2)
        c1.metric("Location", city_name)
        c2.metric("Wind Speed", f"{wind_speed_ms} m/s ({wind_speed_kmh} km/h)")
        
        # 2. The Result
        if is_windy:
            st.success("💨 It is windy! The chime rings.")
            
            # --- MEME VISUALIZATION (Only if windy) ---
            # Shrunk dimensions: Diamond width 2.5, Rectangle width 1.0
            dot_code = f"""
            digraph G {{
                rankdir=TB;
                bgcolor="transparent";
                nodesep=0.5;
                
                node [fontname="Helvetica", style=filled, fillcolor=white, penwidth=2];
                
                Start [shape=diamond, label="風有在吹嗎？\\n(Is the wind blowing?)", width=2.5, height=1.0];
                
                Ding [shape=box, label="\\n\\n叮\\n鈴\\n|\\n\\n(Ding-)", fixedsize=true, width=1.0, height=3.0, fontsize=18, color="red", penwidth=3];
                
                Start:s -> Ding:n [label=" YES ", color="green", fontcolor="green", penwidth=3, style="solid", arrowsize=1.2];
            }}
            """
            st.graphviz_chart(dot_code, use_container_width=True)
            
            # Sound
            if os.path.exists("sounds/furin.mp3"):
                st.audio("sounds/furin.mp3", format="audio/mp3", autoplay=True)
                
        else:
            # --- CALM STATE (No Meme) ---
            st.info("🍂 It is calm. The wind chime sleeps.")
            st.markdown("""
            <div style='font-size: 50px; margin-top: 20px;'>🚫🎐</div>
            """, unsafe_allow_html=True)

        st.write("") # Spacer
        
        # 3. Try Again Button
        # Logic: We keep the coords, just rerun the script to fetch new weather data
        if st.button("🔄 Try Again"):
            st.rerun()
            
        # Reset Button (To choose new location)
        if st.button("📍 Change Location"):
            st.session_state['coords'] = None
            st.rerun()

    else:
        st.error("Could not fetch weather data.")
        if st.button("Back"):
            st.session_state['coords'] = None
            st.rerun()