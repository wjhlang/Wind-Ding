import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

# Load env (local)
load_dotenv()

st.set_page_config(page_title="Wind-ding", page_icon="🎐")

# --- AESTHETIC CSS (Monochrome) ---
st.markdown("""
<style>
    /* 1. FORCE WHITE THEME */
    .stApp {
        background-color: #ffffff;
        color: #000000;
        text-align: center;
        font-family: 'Helvetica', 'Arial', sans-serif;
    }
    
    /* 2. HIDE AUDIO PLAYER */
    .stAudio { display: none; }

    /* 3. STYLING THE GEOLOCATION BUTTON (The Icon Button) */
    div[data-testid="stBlock"] button {
        width: 100px !important;
        height: 100px !important;
        background-color: #000000 !important; /* Black */
        color: white !important;
        border-radius: 50%; /* Circle */
        border: none !important;
        margin: 20px auto !important;
        display: block !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stBlock"] button:hover {
        transform: scale(1.05);
        background-color: #333333 !important;
    }
    
    /* 4. STYLING STANDARD BUTTONS (The 'Back' Button) */
    .stButton button {
        background-color: white !important;
        color: black !important;
        border: 2px solid black !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        margin: 20px auto !important;
        display: block !important;
    }
    .stButton button:hover {
        background-color: black !important;
        color: white !important;
    }

    /* 5. TITLE & TEXT */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -1px;
        color: black !important;
    }
    .instruction-text {
        color: #666;
        font-size: 18px;
        margin-bottom: 10px;
    }

    /* 6. REMOVE STREAMLIT PADDING */
    .block-container {
        padding-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
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
    st.markdown('<p class="instruction-text">Click the button below to check the wind.</p>', unsafe_allow_html=True)
    
    # This renders the geolocation button (Styled as a black circle by CSS above)
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
        is_windy = speed >= 5.0 # Threshold
        
        # --- THE MEME (Black & White, Narrow) ---
        if is_windy:
            # SOUND
            if os.path.exists("sounds/furin.mp3"):
                st.audio("sounds/furin.mp3", format="audio/mp3", autoplay=True)
            
            st.success(f"It is windy ({speed} m/s).")
            
            # Graphviz: Clean B&W lines
            dot = f"""
            digraph G {{
                bgcolor="transparent"; rankdir=TB; nodesep=0.5;
                node [fontname="Helvetica", style=solid, color=black, fontcolor=black, penwidth=2];
                edge [color=black, penwidth=2];

                # Diamond: width=1.8 (Narrower), height=1.0
                Start [shape=diamond, label="風有在吹嗎？\\n(Wind?)", width=1.8, height=1.0, fixedsize=true];
                
                # Chime: width=0.8 (Thin strip), height=3.0
                Ding [shape=box, label="\\n\\n叮\\n鈴\\n|\\n\\n(Ding)", fixedsize=true, width=0.8, height=3.0, fontsize=16];
                
                # Connection
                Start:s -> Ding:n [label=" YES ", fontcolor=black];
            }}
            """
            st.graphviz_chart(dot, use_container_width=True)
            
        else:
            # CALM STATE
            st.info(f"It is calm ({speed} m/s).")
            st.markdown("<div style='font-size: 80px; margin: 30px;'>🍂</div>", unsafe_allow_html=True)
            st.markdown("The wind chime sleeps.")

        # --- RESET BUTTON ---
        st.write("")
        st.write("")
        if st.button("Check Another Location"):
            st.session_state['coords'] = None # Clear state
            st.rerun() # Go back to start
            
    else:
        st.error("Could not fetch weather.")
        if st.button("Back"):
            st.session_state['coords'] = None
            st.rerun()