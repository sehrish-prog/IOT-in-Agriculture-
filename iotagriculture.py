"""
Simple Multi-City IoT Dashboard for Mehrano Agri Farms
Cities: DG Khan, Muzaffargarh (Punjab), Mirpur Khas, Sukkur (Sindh)
Features: Real-time weather, comparison charts, alerts
"""

import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================
API_KEY = "5bae2c88d41917c4d6c7b31759c0e9a3"

# 4 Cities with coordinates
CITIES = {
    "DG Khan": {"lat": 30.0430, "lon": 70.6350, "province": "Punjab"},
    "Muzaffargarh": {"lat": 30.0725, "lon": 71.1933, "province": "Punjab"},
    "Mirpur Khas": {"lat": 25.5276, "lon": 69.0111, "province": "Sindh"},
    "Sukkur": {"lat": 27.7050, "lon": 68.8575, "province": "Sindh"}
}

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Mehrano Agri Farms - Multi-City IoT Dashboard",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Mehrano Agri Farms - Multi-City Smart Farming Dashboard")
st.markdown("*Real-time environmental monitoring for Punjab & Sindh*")
st.markdown("---")

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.header("🎛️ Dashboard Controls")
    
    # Select cities to display
    selected_cities = st.multiselect(
        "Select Cities to Monitor",
        options=list(CITIES.keys()),
        default=["DG Khan", "Muzaffargarh", "Mirpur Khas", "Sukkur"]
    )
    
    update_freq = st.select_slider("Update Frequency (seconds)", options=[15, 30, 60], value=30)
    
    st.markdown("---")
    st.header("📊 Display Options")
    show_comparison = st.checkbox("Show Comparison Charts", value=True)
    show_alerts = st.checkbox("Show Alerts", value=True)
    
    st.markdown("---")
    st.header("📈 Optimal Ranges")
    st.metric("Soil Moisture", "40% - 75%")
    st.metric("Soil pH", "6.5 - 7.5")
    st.metric("Temperature", "< 38°C")
    
    st.markdown("---")
    st.caption("**Unit 20: Internet of Things**")
    st.caption("Mehrano Agri Farms Ltd")

# ============================================
# FUNCTIONS
# ============================================
def get_weather(city_name):
    """Fetch weather data for a city"""
    coords = CITIES[city_name]
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def calculate_soil(weather):
    """Calculate soil moisture from weather"""
    if not weather:
        return None
    
    temp = weather['main']['temp']
    rain = weather.get('rain', {}).get('1h', 0)
    
    # Simple soil moisture calculation
    moisture = 50 - (temp - 25) * 0.7 + rain * 10
    moisture = max(15, min(85, moisture))
    
    # Simple pH calculation
    ph = 7.0 - (rain * 0.02)
    ph = max(6.0, min(8.5, ph))
    
    return {
        'moisture': round(moisture, 1),
        'ph': round(ph, 2)
    }

# ============================================
# SESSION STATE
# ============================================
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# ============================================
# MAIN DISPLAY
# ============================================
placeholder = st.empty()

while True:
    # Fetch data for all selected cities
    all_data = []
    alerts = []
    
    for city in selected_cities:
        weather = get_weather(city)
        if weather:
            st.session_state.weather_data[city] = weather
            soil = calculate_soil(weather)
            
            all_data.append({
                'City': city,
                'Province': CITIES[city]['province'],
                'Temperature (°C)': weather['main']['temp'],
                'Feels Like': weather['main']['feels_like'],
                'Humidity (%)': weather['main']['humidity'],
                'Rainfall (mm)': weather.get('rain', {}).get('1h', 0),
                'Soil Moisture (%)': soil['moisture'],
                'Soil pH': soil['ph']
            })
            
            # Generate alerts
            if soil['moisture'] < 35:
                alerts.append(f"🟠 {city}: Low soil moisture ({soil['moisture']}%)")
            if weather['main']['temp'] > 38:
                alerts.append(f"🟠 {city}: High temperature ({weather['main']['temp']}°C)")
            if soil['ph'] > 8.0:
                alerts.append(f"🟠 {city}: High pH ({soil['ph']})")
            if soil['ph'] < 6.5:
                alerts.append(f"🟠 {city}: Low pH ({soil['ph']})")
    
    current_time = datetime.now()
    df = pd.DataFrame(all_data)
    
    with placeholder.container():
        
        # Header
        st.markdown(f"### 📡 Last Updated: {current_time.strftime('%H:%M:%S')}")
        st.markdown(f"**Cities:** {', '.join(selected_cities)}")
        st.markdown("---")
        
        # ============================================
        # CITY CARDS (4 Columns)
        # ============================================
        st.markdown("## 📍 Current Conditions by City")
        
        cols = st.columns(len(selected_cities))
        
        for idx, city in enumerate(selected_cities):
            with cols[idx]:
                city_data = next((item for item in all_data if item['City'] == city), None)
                if city_data:
                    st.markdown(f"### {city}")
                    st.markdown(f"*{CITIES[city]['province']}*")
                    st.markdown("---")
                    st.metric("🌡️ Temperature", f"{city_data['Temperature (°C)']}°C")
                    st.metric("💧 Humidity", f"{city_data['Humidity (%)']}%")
                    st.metric("☔ Rainfall", f"{city_data['Rainfall (mm)']} mm")
                    st.metric("💧 Soil Moisture", f"{city_data['Soil Moisture (%)']}%")
                    st.metric("🧪 Soil pH", f"{city_data['Soil pH']}")
                    
                    # Simple gauge for soil moisture
                    moisture = city_data['Soil Moisture (%)']
                    if moisture < 35:
                        st.progress(moisture, text=f"⚠️ Low: {moisture}%")
                    elif moisture > 75:
                        st.progress(moisture, text=f"💧 High: {moisture}%")
                    else:
                        st.progress(moisture / 100, text=f"Optimal: {moisture}%")
        st.markdown("---")
        
        # ============================================
        # COMPARISON CHARTS
        # ============================================
        if show_comparison and len(df) > 1:
            st.markdown("## 📊 City Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🌡️ Temperature Comparison**")
                st.bar_chart(df.set_index('City')['Temperature (°C)'])
            
            with col2:
                st.markdown("**💧 Soil Moisture Comparison**")
                st.bar_chart(df.set_index('City')['Soil Moisture (%)'])
            
            # Simple data table
            st.markdown("**📋 Detailed Data Table**")
            st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        # ============================================
        # ALERTS
        # ============================================
        if show_alerts:
            st.markdown("## ⚠️ Alerts & Recommendations")
            
            if alerts:
                for alert in alerts:
                    st.warning(alert)
                
                # Summary
                st.markdown("---")
                st.markdown("### 💡 Summary Actions")
                low_moisture_cities = [a for a in alerts if 'Low soil moisture' in a]
                high_temp_cities = [a for a in alerts if 'High temperature' in a]
                
                if low_moisture_cities:
                    st.write(f"💧 **Irrigation needed:** {len(low_moisture_cities)} cities")
                if high_temp_cities:
                    st.write(f"🔥 **Heat stress risk:** {len(high_temp_cities)} cities")
            else:
                st.success("✅ All systems normal - No active alerts")
        
        st.markdown("---")
        
        # ============================================
        # RECOMMENDATIONS
        # ============================================
        st.markdown("## 💡 Smart Farming Recommendations")
        
        for city_data in all_data:
            city = city_data['City']
            moisture = city_data['Soil Moisture (%)']
            temp = city_data['Temperature (°C)']
            ph = city_data['Soil pH']
            
            st.markdown(f"**📍 {city}**")
            
            if moisture < 35:
                st.write(f"💧 **Irrigation:** Needed immediately (moisture: {moisture}%)")
            elif moisture < 50:
                st.write(f"💧 **Irrigation:** Schedule within 2-3 days")
            else:
                st.write(f"💧 **Irrigation:** Not needed")
            
            if temp > 38:
                st.write(f"🔥 **Heat Stress:** Increase water supply")
            
            if ph > 8.0:
                st.write(f"🧪 **Soil Treatment:** Apply sulfur to lower pH")
            elif ph < 6.5:
                st.write(f"🧪 **Soil Treatment:** Apply lime to raise pH")
            
            st.markdown("---")
        
        # ============================================
        # FOOTER
        # ============================================
        with st.expander("📡 Raw API Data"):
            for city in selected_cities:
                if city in st.session_state.weather_data:
                    st.markdown(f"**{city}**")
                    st.json(st.session_state.weather_data[city])
                    st.markdown("---")
        
        st.caption(f"🔄 Auto-refreshes every {update_freq} seconds")
    
    time.sleep(update_freq)