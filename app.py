import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

# Load env (local only)
load_dotenv()

st.set_page_config(page_title="Wind-ding", page_icon="🎐")

# --- CSS: FORCE WHITE THEME & STYLING ---
st.markdown("""
<style>
    /* 1. Force White Background & Black Text */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        text-align: center;
    }
    
    /* 2. Hide the Audio Player UI */
    .stAudio { display: none; }
    
    /* 3. Style the Geolocation Button to look like "Ring It" */
    div[data-testid="stBlock"] button {
        width: 220px !important;
        height: 60px !important;
        background-color: #000000 !important; /* Black button */
        color: transparent !important;
        border-radius: 30px !important;
        border: none !important;
        margin: 20px auto !important;
        display: block !important;
        position: relative;
    }
    
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

    /* 4. Center normal buttons (Try Again) */
    .stButton button {
        margin: 0 auto;
        display: block;
        background-color: white;
        color: black;
        border: 2px solid black;
    }
    .stButton button:hover {
        border-color: #333;
        background-color: #f0f0f0;
        color: black;
    }

    /* Title */
    .big-title { 
        font-size: 32px !important; 
        font-weight: bold; 
        font-family: sans-serif;
        color: black;
        margin-bottom: 5px;
    }
    
    /* Metric Labels */
    div[data-testid="stMetricLabel"] { color: #555 !important; }
    div[data-testid="stMetricValue"] { color: #000 !important; }
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

# --- SETUP ---
api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
if not api_key:
    st.error("⚠️ API Key missing.")
    st.stop()

# Session State
if 'coords' not in st.session_state:
    st.session_state['coords'] = None
if 'refresh_trigger' not in st.session_state:
    st.session_state['refresh_trigger'] = 0

# --- MAIN APP ---

st.markdown('<div class="big-title">這個是風鈴 (This is Wind-ding)</div>', unsafe_allow_html=True)

# Placeholder ensures we can wipe the button off the screen completely
main_placeholder = st.empty()

# PHASE 1: GET LOCATION
if st.session_state['coords'] is None:
    with main_placeholder.container():
        st.write("Click below to check the wind.")
        # The CSS above turns this into the "Ring It" button
        location = streamlit_geolocation()
        
        if location and location['latitude'] is not None:
            st.session_state['coords'] = {'lat': location['latitude'], 'lon': location['longitude']}
            st.rerun()

# PHASE 2: RESULT
else:
    # Clear Phase 1 content immediately
    main_placeholder.empty()
    
    lat = st.session_state['coords']['lat']
    lon = st.session_state['coords']['lon']
    
    # Spinner for "Try Again" feeling
    with st.spinner("Listening to the wind..."):
        # Artificial delay so "Try Again" feels like it's doing work
        time.sleep(0.5) 
        data = get_weather_by_coords(lat, lon, api_key)

    if data:
        wind_speed_ms = data['wind']['speed']
        wind_speed_kmh = round(wind_speed_ms * 3.6, 1)
        city_name = data['name']
        threshold = 5.0
        is_windy = wind_speed_ms >= threshold
        
        # --- DISPLAY ---
        
        # 1. Metrics (Simple Black Text)
        c1, c2 = st.columns(2)
        c1.metric("Location", city_name)
        c2.metric("Wind Speed", f"{wind_speed_ms} m/s")
        
        # 2. Logic
        if is_windy:
            st.success(f"It is windy ({wind_speed_kmh} km/h). The chime rings.")
            
            # --- MEME (B/W, Small Diamond) ---
            # shape=diamond width=1.8 (Shrunk horizontally)
            # color=black for all lines
            dot_code = f"""
            digraph G {{
                rankdir=TB;
                bgcolor="white";
                nodesep=0.5;
                
                node [fontname="Helvetica", style=solid, color=black, fontcolor=black, penwidth=1.5];
                edge [color=black, penwidth=1.5, arrowsize=1.0];
                
                # Diamond: width=1.8 (Small), height=0.8
                Start [shape=diamond, label="風有在吹嗎？\\n(Is the wind blowing?)", width=1.8, height=0.8];
                
                # Chime: width=0.8, height=3.0
                Ding [shape=box, label="\\n\\n叮\\n鈴\\n|\\n\\n(Ding-)", fixedsize=true, width=0.8, height=3.0, fontsize=18];
                
                # Connection
                Start:s -> Ding:n [label=" YES ", fontcolor=black, style=solid];
            }}
            """
            st.graphviz_chart(dot_code, use_container_width=True)
            
            # --- SOUND FIX ---
            if os.path.exists("sounds/furin.mp3"):
                # We add a unique 'key' using time.time(). 
                # This forces Streamlit to destroy and recreate the audio player.
                # This tricks the browser into playing the sound again on 'Try Again'.
                st.audio("sounds/furin.mp3", format="audio/mp3", autoplay=True, start_time=0)
                
        else:
            # Calm State
            st.info(f"It is calm ({wind_speed_kmh} km/h).")
            # Simple line art for "Calm"
            st.markdown("""
            <div style='font-size: 60px; margin-top: 20px; filter: grayscale(100%);'>🍂</div>
            """, unsafe_allow_html=True)

        st.write("") # Spacer
        
        # 3. Try Again Button
        # This will just rerun the script. 
        # Because we added the time.sleep and spinner above, and the unique key to audio, 
        # it will feel like a real refresh.
        if st.button("🔄 Try Again"):
            st.session_state['refresh_trigger'] += 1 # dummy change to force state update
            st.rerun()
            
        if st.button("📍 Change Location"):
            st.session_state['coords'] = None
            st.rerun()

    else:
        st.error("Error fetching weather.")
        if st.button("Back"):
            st.session_state['coords'] = None
            st.rerun()