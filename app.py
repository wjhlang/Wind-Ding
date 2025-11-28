import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

# Load env (for local testing)
load_dotenv()

st.set_page_config(page_title="Wind-ding", page_icon="🎐")

# --- CSS STYLING ---
st.markdown("""
<style>
    /* 1. Global White Theme */
    .stApp {
        background-color: #ffffff;
        color: #000000;
        text-align: center;
    }
    
    /* 2. Hide Audio Player */
    .stAudio { display: none; }

    /* 3. "Ring It" Button Styling (Phase 1) */
    /* We target the FIRST button on the screen specifically */
    div.row-widget.stButton > button {
        width: 100%;
        max-width: 300px;
        margin: 0 auto;
        border-radius: 50px;
        height: 60px;
        background-color: #000000; /* Black Button */
        color: transparent !important; /* Hide original text */
        position: relative;
        border: none;
    }
    
    /* Overlay "Ring It" text */
    div.row-widget.stButton > button::before {
        content: "🎐 Ring It";
        color: white;
        font-size: 22px;
        font-weight: bold;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
    }

    /* 4. Style 'Try Again' buttons differently (Phase 2) */
    /* Since Phase 2 buttons are standard, we override the styling below in Python logic 
       by using columns or specific placement, but CSS overrides are global. 
       To avoid conflict, we live with the Black 'Ring It' style for all buttons 
       OR we accept that 'Try Again' will also look like a cool black button. 
       (It looks better if they match anyway!) 
    */
    
    /* Change text for Try Again buttons dynamically? 
       CSS is static. We will override the ::before content for the bottom buttons 
       using a specific Streamlit container hack if needed, but for now, 
       let's let the bottom buttons use their natural text color by overriding the ::before 
       if possible. Actually, simpler: We only apply the 'Ring It' hack to the TOP button.
    */
    
    /* HACK: Only apply the 'Ring It' text overlay to the first button in the app */
    div.element-container:nth-of-type(2) button::before {
         /* This targets the geolocation button specifically usually */
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

def reset_weather():
    """Forces the app to forget the current weather but keep the location"""
    st.session_state['weather_data'] = None
    st.session_state['audio_trigger'] = str(time.time()) # New ID to force sound reload

# --- SETUP ---
api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
if not api_key:
    st.error("⚠️ API Key missing.")
    st.stop()

# Initialize Session State
if 'coords' not in st.session_state:
    st.session_state['coords'] = None
if 'weather_data' not in st.session_state:
    st.session_state['weather_data'] = None
if 'audio_trigger' not in st.session_state:
    st.session_state['audio_trigger'] = "0"

# --- MAIN APP ---

st.markdown('<h1 style="text-align: center; color: black;">這個是風鈴 (This is Wind-ding)</h1>', unsafe_allow_html=True)

# PHASE 1: NO LOCATION
if st.session_state['coords'] is None:
    st.write("Click below to check the wind.")
    
    # This button gets the "Ring It" CSS styling because it is the first button
    loc = streamlit_geolocation()
    
    if loc and loc['latitude'] is not None:
        st.session_state['coords'] = {'lat': loc['latitude'], 'lon': loc['longitude']}
        st.rerun()

# PHASE 2: LOCATION FOUND
else:
    # 1. Fetch Weather (if we don't have it yet)
    if st.session_state['weather_data'] is None:
        with st.spinner("Checking the wind..."):
            time.sleep(1.0) # Fake delay so you SEE the "Try Again" working
            lat = st.session_state['coords']['lat']
            lon = st.session_state['coords']['lon']
            data = get_weather(lat, lon, api_key)
            st.session_state['weather_data'] = data
            st.rerun() # Refresh to show data

    # 2. Show Data
    data = st.session_state['weather_data']
    if data:
        speed = data['wind']['speed']
        is_windy = speed >= 5.0 # Threshold
        
        # --- MEME VISUALIZATION ---
        if is_windy:
            # Windy State
            dot = f"""
            digraph G {{
                bgcolor="white"; rankdir=TB; nodesep=0.5;
                node [fontname="Helvetica", style=solid, color=black, fontcolor=black, penwidth=1.5];
                edge [color=black, penwidth=1.5];

                # Diamond: width=1.5 (NARROW), height=1.0, fixedsize=true
                Start [shape=diamond, label="風有在吹嗎？\\n(Wind?)", width=1.5, height=1.0, fixedsize=true];
                
                # Chime
                Ding [shape=box, label="\\n\\n叮\\n鈴\\n|\\n\\n(Ding)", fixedsize=true, width=0.8, height=3.0, fontsize=16];
                
                Start:s -> Ding:n [label=" YES "];
            }}
            """
            st.graphviz_chart(dot, use_container_width=True)
            st.success(f"It is windy ({speed} m/s). The chime rings.")
            
            # Sound: Uses unique key to force replay
            if os.path.exists("sounds/furin.mp3"):
                st.audio("sounds/furin.mp3", format="audio/mp3", autoplay=True, start_time=0)
                
        else:
            # Calm State
            st.markdown("<br><br><div style='font-size: 60px;'>🍂</div>", unsafe_allow_html=True)
            st.info(f"It is calm ({speed} m/s).")

        st.markdown("---")

        # --- BUTTONS ---
        # Note: CSS makes buttons black/transparent by default. 
        # We need to hack the "Try Again" buttons to show text properly if the CSS is too aggressive.
        # But for now, the "Ring It" text only applies to the top button if structured correctly.
        # Let's use a standard grid for buttons.
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Try Again"):
                reset_weather()
                st.rerun()
        with c2:
            if st.button("📍 Change Location"):
                st.session_state['coords'] = None
                st.session_state['weather_data'] = None
                st.rerun()
                
    else:
        st.error("Error fetching weather.")
        if st.button("Reset"):
            st.session_state['coords'] = None
            st.rerun()