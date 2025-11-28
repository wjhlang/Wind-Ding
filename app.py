import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation
import random

# Load env (local)
load_dotenv()

st.set_page_config(page_title="Wind-Ding", page_icon="🎐", layout="centered")

# --- CSS: FINAL POLISH ---
st.markdown("""
<style>
    /* 1. FORCE THEME: WHITE BACKGROUND */
    .stApp {
        background-color: #ffffff;
        color: #000000;
        font-family: sans-serif;
    }
    
    /* 2. HIDE HEADER & AUDIO PLAYER */
    header[data-testid="stHeader"] { display: none; }
    .stAudio { display: none; }

    /* 3. BUTTON STYLING */
    button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        box-shadow: none !important;
        transition: all 0.2s;
        
        /* FIX THE BLACK BAR: Force button to shrink to content */
        width: auto !important; 
        min-width: 100px !important;
    }
    
    button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    
    button svg {
        fill: currentColor !important;
    }

    /* 4. REMOVE GHOST BARS & FORCE CENTERING */
    /* This removes background from the button's container div */
    div.row-widget.stButton {
        text-align: center;
        background: transparent !important;
    }
    div[data-testid="stBlock"] {
        background: transparent !important;
    }
    
    /* Force content inside columns to center */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* 5. METRICS TEXT COLOR */
    div[data-testid="stMetricLabel"] { color: #666 !important; font-size: 14px !important; }
    div[data-testid="stMetricValue"] { color: #000 !important; }

    /* 6. TITLE STYLE */
    h1 {
        color: black !important;
        text-align: center;
        padding-top: 20px;
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

st.title("This is Wind-Ding")

# === STATE 1: START SCREEN ===
if st.session_state['coords'] is None:
    st.markdown("<p style='text-align: center; color: #333;'>Click the button below to check the wind.</p>", unsafe_allow_html=True)
    st.write("") 

    # CENTER BUTTON using Columns
    # The CSS rule #6 above ensures the contents of this middle column are centered flex-wise
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
        
        # --- CUSTOM HTML METRICS ---
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"""
            <div style="text-align: center;">
                <p style="color: #666; margin: 0; font-size: 14px;">Location</p>
                <p style="color: #000; margin: 0; font-size: 24px; font-weight: bold;">{city}</p>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div style="text-align: center;">
                <p style="color: #666; margin: 0; font-size: 14px;">Wind Speed</p>
                <p style="color: #000; margin: 0; font-size: 24px; font-weight: bold;">{speed} m/s</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 25px 0; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)
        
        # --- THE MEME ---
        if is_windy:
            # RANDOM SOUND LOGIC
            if os.path.exists("sounds"):
                # List all files in 'sounds' folder that end with .mp3
                sound_files = [f for f in os.listdir("sounds") if f.endswith(".mp3")]
                
                if sound_files:
                    # Pick a random file
                    random_sound = random.choice(sound_files)
                    st.audio(f"sounds/{random_sound}", format="audio/mp3", autoplay=True)
                else:
                    st.warning("No MP3 files found in 'sounds' folder.")

            col_left, col_mid, col_right = st.columns([1, 4, 1]) # Wider middle column for graph
            with col_mid:
                # CHANGES HERE: fontsize=9, width=1.5
                dot = f"""
                digraph G {{
                    bgcolor="transparent"; rankdir=TB; nodesep=0.3;
                    
                    # Global settings
                    node [fontname="Arial", style=solid, color=black, fontcolor=black, penwidth=1.0, fontsize=10];
                    edge [color=black, penwidth=1.0, arrowsize=0.6];

                    # Diamond: Wider (1.5) and Smaller Font (fontsize=9)
                    Start [shape=diamond, label="Is the wind blowing?", fontsize=9, width=1.5, height=0.7, fixedsize=true];
                    
                    # Chime
                    Ding [shape=box, label="Ding\\n|", fixedsize=true, width=0.6, height=2.2, fontsize=11];
                    
                    Start:s -> Ding:n [label=" YES ", fontcolor=black, fontsize=9];
                }}
                """
                st.graphviz_chart(dot, use_container_width=True)
                st.markdown("", unsafe_allow_html=True)
            
        else:
            # CALM STATE
            col_left, col_mid, col_right = st.columns([1, 2, 1])
            with col_mid:
                st.markdown("<div style='font-size: 60px; margin: 20px; text-align: center;'>🍂</div>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: black; font-weight: bold;'>It is calm.</p>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #555;'>The wind chime sleeps.</p>", unsafe_allow_html=True)

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