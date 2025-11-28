import time
import requests
from playsound import playsound # Library to play audio
import json

# --- CONFIGURATION ---
# Get a free key from https://openweathermap.org/api
API_KEY = "1dab3be01f2c798b87ce617ed897e082" 

# Wind threshold in meters/second to trigger the ding
WIND_THRESHOLD = 5.0

# How often to check (in seconds).
CHECK_INTERVAL = 600  # 10 minutes

def get_user_location():
    """
    Automatically detects the user's city based on their IP address.
    """
    try:
        print("🌍 Detecting location...")
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        city = data.get("city")
        country = data.get("country")
        print(f"📍 Location found: {city}, {country}")
        return city
    except Exception as e:
        print("❌ Could not detect location. Defaulting to London.")
        return "London"

def check_weather(city):
    """
    Checks the current weather for the specific city.
    Returns the wind speed.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            wind_speed = data['wind']['speed']
            return wind_speed
        else:
            print(f"⚠️ Error getting weather: {data.get('message', 'Unknown error')}")
            return 0
    except Exception as e:
        print(f"⚠️ Connection error: {e}")
        return 0

def wind_ding():
    print("🎐 Starting Wind-ding System...")
    
    # 1. Detect Location once at startup
    city = get_user_location()
    
    while True:
        print(f"\n☁️  Checking wind in {city}...")
        
        # 2. Check Wind Speed
        current_wind = check_weather(city)
        print(f"💨 Current Wind Speed: {current_wind} m/s")
        
        # 3. Logic: Is wind > Threshold?
        if current_wind >= WIND_THRESHOLD:
            print("🎐 YES! It is windy. *DING*")
            try:
                # Play the chime sound
                playsound('furin.mp3')
            except Exception as e:
                print("Error playing sound. Make sure 'furin.mp3' is in the folder.")
        else:
            print("🍂 No. It is calm.")
            
        # Wait before checking again
        print(f"⏳ Waiting {CHECK_INTERVAL/60} minutes for next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    wind_ding()