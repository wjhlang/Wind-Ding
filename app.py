import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

# Load env (local)
load_dotenv()

st.set_page_config(page_title="Wind-ding", page_icon="🎐")

# --- CSS: CLEAN WHITE THEME ---
st.markdown("""
<style>
    /* 1. FORCE WHITE THEME & BLACK TEXT */
    .stApp {
        background-color: #ffffff;
        color: #000000;
        text-align: center;
    }
    
    /* 2. HIDE AUDIO PLAYER */
    .stAudio { display: none; }

    /* 3. CENTER & STYLE ALL BUTTONS (Streamline Look) */
    .stButton button, div[data-testid="stBlock"] button {
        background-color: white !important;
        color: black !important;
        border: 2px solid black !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        margin: 0 auto !important;
        display: block !important;
        transition: all 0.2s;
    }
    
    /* Hover Effect: Turn Black */
    .stButton button:hover, div[data-testid="stBlock"] button:hover {
        background-color: black !important;
        color: white !important;
        border-color: black !important;
    }
    
    /* Fix the SVG Icon inside the geolocation button to swap colors too */
    div[data-testid="stBlock"] button svg {
        fill: currentColor !important;
    }
    
    /* 4. TITLE STYLE */
    h1 {
        color: black !important;
        font-weight: 700 !important;
        font-family: sans-serif;
    }
    
    /* 5. METRICS STYLE (Restoring the labels) */
    div[data-testid="stMetricLabel"] { 
        color: #666 !important; /* Grey color for the small label */
        font-size: 14px !important;
        font-weight: normal !important;
    }
    div[data-testid="stMetricValue"] { 
        color: #000 !important; /* Black color for the value */
        font-weight: bold !important;
    }

</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_weather(lat, lon, key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric"
        res = requests.get(url)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# --- SETUP ---
api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
if not api_key:
    st.error("⚠️ API Key missing.")
    st.stop()

if 'coords' not in st.session_state:
    st.session_state['coords'] = None

# --- MAIN UI ---

st.title("This is Wind-ding")

# === STATE 1: START SCREEN ===
if st.session_state['coords'] is None:
    st.write("Click the button below to check the wind.")
    st.write("") # Spacer

    # Use Columns to center the button
    c1, c2, c3 = st.columns([3, 1, 3])
    
    with c2:
        # The Geolocation button (Now White with Black Border)
        loc = streamlit_geolocation()
    
    if loc and loc['latitude'] is not None:
        st.session_state['coords'] = {'lat': loc['latitude'], 'lon': loc['longitude']}
        st.rerun()

# === STATE 2: RESULT SCREEN ===
else:
    lat = st.session_state['coords']['lat']
    lon = st.session_state['coords']['lon']
    
    # Fetch Data
    data = get_weather(lat, lon, api_key)
    
    if data:
        speed = data['wind']['speed']
        city = data['name']
        is_windy = speed >= 5.0 # Threshold
        
        # --- SHOW METRICS ---
        m1, m2 = st.columns(2)
        m1.metric("Location", city)
        m2.metric("Wind Speed", f"{speed} m/s")
        
        st.write("---") # Divider line
        
        # --- THE MEME ---
        if is_windy:
            # PLAY SOUND
            if os.path.exists("sounds/furin.mp3"):
                st.audio("sounds/furin.mp3", format="audio/mp3", autoplay=True)
            
            # MEME GRAPH (Thinner strokes, smaller font)
            dot = f"""
            digraph G {{
                bgcolor="transparent"; rankdir=TB; nodesep=0.5;
                
                # Global Node Settings: Thinner lines (penwidth=1), smaller font (fontsize=12)
                node [fontname="Arial", style=solid, color=black, fontcolor=black, penwidth=1.0, fontsize=10];
                edge [color=black, penwidth=1.0];

                # Diamond: Narrow width
                Start [shape=diamond, label="Is the wind blowing?", width=1.2, height=0.8, fixedsize=true];
                
                # Chime: Thin strip
                Ding [shape=box, label="Ding", fixedsize=true, width=0.8, height=3.0, fontsize=12];
                
                # Connection
                Start:s -> Ding:n [label="YES", fontcolor=black, arrowsize=1];
            }}
            """
            st.graphviz_chart(dot, use_container_width=True)
            st.success('Ding')
            
        else:
            # CALM STATE
            st.info("It is calm.")
            st.markdown("<div style='font-size: 80px; margin: 30px;'>🍂</div>", unsafe_allow_html=True)
            st.write("The wind chime sleeps.")

        # --- RESET BUTTON ---
        st.write("")
        st.write("")
        if st.button("Check Another Location"):
            st.session_state['coords'] = None
            st.rerun()
            
    else:
        st.error("Could not fetch weather.")
        if st.button("Back"):
            st.session_state['coords'] = None
            st.rerun()