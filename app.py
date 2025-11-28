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
    /* 1. CENTER EVERYTHING */
    .stApp { text-align: center; }
    
    /* 2. HIDE THE AUDIO PLAYER (But let it play) */
    .stAudio { display: none; }
    
    /* 3. CUSTOMIZE THE GEOLOCATION BUTTON */
    /* This targets the specific button created by the geolocation library */
    div[data-testid="stBlock"] button {
        width: 200px !important;
        height: 80px !important;
        background-color: #4CAF50 !important; /* Green color */
        border-radius: 50px !important;
        border: none !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* This adds the text "Ring It" to the button using CSS */
    div[data-testid="stBlock"] button::after {
        content: "🎐 Ring It"; 
        font-size: 25px;
        font-weight: bold;
        color: white;
        display: block;
    }
    
    /* Hide the original tiny icon inside the button */
    div[data-testid="stBlock"] button svg {
        display: none !important;
    }

    /* Title Styling */
    .big-title { 
        font-size: 40px !important; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 10px;
        font-family: sans-serif;
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

# --- LAYOUT LOGIC ---

# 1. We create a placeholder. We will put the button here.
#    Once clicked, we will empty this placeholder so the button vanishes.
button_placeholder = st.empty()
meme_placeholder = st.empty()

# 2. Check if we already have data in session state (to keep meme on screen)
if 'weather_data' not in st.session_state:
    st.session_state['weather_data'] = None

# 3. RENDER THE BUTTON (Only if we don't have data yet)
location = None
if st.session_state['weather_data'] is None:
    with button_placeholder.container():
        st.markdown('<div class="big-title">This is Wind-ding</div>', unsafe_allow_html=True)
        st.write("Click below to check the wind.")
        st.write("") # Spacer
        
        # This creates the button. 
        # Note: We centered it using the CSS above (margin: 0 auto).
        location = streamlit_geolocation()

# 4. PROCESS LOGIC
if location and location['latitude'] is not None:
    # If user just clicked, fetch data and save to session
    lat = location['latitude']
    lon = location['longitude']
    data = get_weather_by_coords(lat, lon, api_key)
    st.session_state['weather_data'] = data
    
    # Rerun to clear the button immediately
    st.rerun()

# 5. SHOW THE MEME (If we have data)
if st.session_state['weather_data']:
    # Clear the button placeholder just in case
    button_placeholder.empty()
    
    data = st.session_state['weather_data']
    wind_speed = data['wind']['speed']
    threshold = 5.0 
    is_windy = wind_speed >= threshold
    
    # Colors
    graph_color = "green" if is_windy else "black"
    ding_color = "red" if is_windy else "grey"
    edge_style = "solid" if is_windy else "dashed"
    
    # GRAPHVIZ: Centered and tuned
    # 'Start:s' means the line starts at the SOUTH of the diamond
    # 'Ding:n' means the line ends at the NORTH of the rectangle
    dot_code = f"""
    digraph G {{
        rankdir=TB;
        bgcolor="transparent";
        nodesep=0.5;
        
        node [fontname="Helvetica", style=filled, fillcolor=white, penwidth=2];
        
        # Diamond: width=3, height=1 (Shrunk based on your feedback)
        Start [shape=diamond, label="Is the wind blowing?", width=3, height=1.2];
        
        # Rectangle: width=1.2 (Narrower), height=4 (Tall)
        Ding [shape=box, label="\\nDing-", fixedsize=true, width=1.2, height=4, fontsize=20, color="{ding_color}", penwidth=3];
        
        # The Edge: Explicitly connecting South to North
        Start:s -> Ding:n [label=" YES ", color="{graph_color}", fontcolor="{graph_color}", penwidth=3, style="{edge_style}", arrowsize=1.5];
    }}
    """
    
    with meme_placeholder.container():
        st.markdown('<div class="big-title">這個是風鈴 (This is Wind-ding)</div>', unsafe_allow_html=True)
        st.graphviz_chart(dot_code, use_container_width=True)
        
        # Metrics
        c1, c2 = st.columns(2)
        c1.metric("Location", data['name'])
        c2.metric("Wind Speed", f"{wind_speed} m/s")
        
        if is_windy:
            st.success("It is windy! The chime rings.")
            if os.path.exists("sounds/furin.mp3"):
                # This audio player is now hidden by CSS, but will autoplay
                st.audio("sounds/furin.mp3", format="audio/mp3", autoplay=True)
        else:
            st.info("It is calm.")
            
    # Button to reset
    if st.button("Try Again"):
        st.session_state['weather_data'] = None
        st.rerun()