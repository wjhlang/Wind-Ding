import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

# Load env (local)
load_dotenv()

st.set_page_config(page_title="Wind-ding", page_icon="🎐")

# --- CSS: PERFECT WHITE THEME & FIXES ---
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

    /* 3. FIX METRIC COLORS (Make them visible!) */
    div[data-testid="stMetricLabel"] {
        color: #666666 !important; /* Label is Grey */
        font-size: 14px !important;
    }
    div[data-testid="stMetricValue"] {
        color: #000000 !important; /* Number is Black */
        font-weight: bold !important;
    }

    /* 4. BUTTON STYLING (Fixing the Black Bar) */
    /* This targets ALL buttons, including the geolocation one */
    button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important; /* Black border */
        border-radius: 8px !important;
        padding: 5px 15px !important;
        margin: 0 auto !important;
        box-shadow: none !important;
    }
    
    /* Remove any weird background fill that creates the 'bar' */
    div[data-testid="stBlock"] button {
        width: auto !important; /* Don't stretch */
        background: white !important;
    }

    button:hover {
        background-color: #f0f0f0 !important;
        border-color: #000000 !important;
        color: #000000 !important;
    }

    /* 5. TITLE STYLE */
    h1 {
        color: black !important;
        font-family: sans-serif;
        font-size: 32px !important;
    }
    
    /* 6. CENTER IMAGES/GRAPHS */
    div[data-testid="stGraphVizChart"] {
        display: flex;
        justify-content: center;
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
        # The Geolocation button (Now Clean White with Black Border)
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
            
            # MEME GRAPH (Smaller, Thinner, Tighter)
            dot = f"""
            digraph G {{
                bgcolor="transparent"; rankdir=TB; nodesep=0.3;
                
                # Global Settings: Thinner lines, Smaller Font
                node [fontname="Arial", style=solid, color=black, fontcolor=black, penwidth=1.0, fontsize=11];
                edge [color=black, penwidth=1.0, arrowsize=0.6]; # Smaller Arrow Head

                # Diamond: Significantly smaller
                Start [shape=diamond, label="風有在吹嗎？\\n(Wind?)", width=1.0, height=0.6, fixedsize=true];
                
                # Chime: Shorter and thinner
                Ding [shape=box, label="\\n\\n叮\\n鈴\\n|\\n\\n(Ding)", fixedsize=true, width=0.6, height=2.2, fontsize=11];
                
                # Connection
                Start:s -> Ding:n [label=" YES ", fontcolor=black, fontsize=9];
            }}
            """
            st.graphviz_chart(dot, use_container_width=False) # False keeps it small/centered
            
            # CLEAN TEXT STATUS (No Green Bar)
            st.markdown("**The chime rings.**")
            
        else:
            # CALM STATE
            st.markdown("<div style='font-size: 60px; margin: 20px;'>🍂</div>", unsafe_allow_html=True)
            st.markdown("**It is calm.**")
            st.markdown("The wind chime sleeps.")

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