import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

# Load env (local)
load_dotenv()

st.set_page_config(page_title="Wind-ding", page_icon="🎐")

# --- CSS: THE "FORCE BLACK TEXT" UPDATE ---
st.markdown("""
<style>
    /* 1. FORCE GLOBAL WHITE THEME */
    .stApp {
        background-color: #ffffff;
        color: #000000;
        text-align: center;
    }
    
    /* 2. HIDE AUDIO PLAYER */
    .stAudio { display: none; }

    /* 3. FIX METRIC LABELS (Aggressive Selector) */
    /* Target the container, the label, and the value specifically */
    div[data-testid="stMetricLabel"] {
        color: #555555 !important; /* Dark Grey */
        font-size: 14px !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #555555 !important; /* Force the paragraph tag inside to be grey */
    }
    div[data-testid="stMetricValue"] {
        color: #000000 !important; /* Black */
    }
    div[data-testid="stMetricValue"] div {
        color: #000000 !important;
    }

    /* 4. BUTTON STYLING */
    /* Universal Button Style: White with Black Border */
    button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        padding: 5px 15px !important;
        margin: 0 auto !important;
        box-shadow: none !important;
    }
    div[data-testid="stBlock"] button {
        background: white !important;
        width: auto !important;
    }
    button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    /* 5. TITLE STYLE */
    h1 {
        color: black !important;
        font-family: sans-serif;
        font-size: 32px !important;
        text-align: center;
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
    st.write("") 

    # CENTER LAYOUT: [1, 1, 1] means 3 equal columns. We put button in the middle.
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c2:
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
        # Note: Metrics auto-center content usually, but the labels need the CSS above
        m1, m2 = st.columns(2)
        m1.metric("Location", city)
        m2.metric("Wind Speed", f"{speed} m/s")
        
        st.write("---") 
        
        # --- THE MEME ---
        if is_windy:
            if os.path.exists("sounds/furin.mp3"):
                st.audio("sounds/furin.mp3", format="audio/mp3", autoplay=True)
            
            # CENTER THE MEME USING COLUMNS
            # [1, 2, 1] makes the middle column 50% width, effectively centering the content
            col_left, col_mid, col_right = st.columns([1, 2, 1])
            
            with col_mid:
                dot = f"""
                digraph G {{
                    bgcolor="transparent"; rankdir=TB; nodesep=0.3;
                    
                    node [fontname="Arial", style=solid, color=black, fontcolor=black, penwidth=1.0, fontsize=11];
                    edge [color=black, penwidth=1.0, arrowsize=0.6];

                    Start [shape=diamond, label="風有在吹嗎？\\n(Wind?)", width=1.0, height=0.6, fixedsize=true];
                    Ding [shape=box, label="\\n\\n叮\\n鈴\\n|\\n\\n(Ding)", fixedsize=true, width=0.6, height=2.2, fontsize=11];
                    
                    Start:s -> Ding:n [label=" YES ", fontcolor=black, fontsize=9];
                }}
                """
                st.graphviz_chart(dot, use_container_width=True)
                
                # Centered Text
                st.markdown("<p style='text-align: center; font-weight: bold;'>The chime rings.</p>", unsafe_allow_html=True)
            
        else:
            # CALM STATE
            col_left, col_mid, col_right = st.columns([1, 2, 1])
            with col_mid:
                st.markdown("<div style='font-size: 60px; margin: 20px; text-align: center;'>🍂</div>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; font-weight: bold;'>It is calm.</p>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center;'>The wind chime sleeps.</p>", unsafe_allow_html=True)

        # --- RESET BUTTON ---
        st.write("")
        st.write("")
        
        # CENTER THE BUTTON USING COLUMNS
        b1, b2, b3 = st.columns([1, 1, 1])
        with b2:
            if st.button("Check Another Location"):
                st.session_state['coords'] = None
                st.rerun()
            
    else:
        st.error("Could not fetch weather.")
        if st.button("Back"):
            st.session_state['coords'] = None
            st.rerun()