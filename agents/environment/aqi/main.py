from typing import Dict, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AQIResponse(BaseModel):
    success: bool
    data: Dict[str, float]
    status: str
    expiresAt: str

class ExtractSchema(BaseModel):
    aqi: float = Field(description="Air Quality Index")
    temperature: float = Field(description="Temperature in degrees Celsius")
    humidity: float = Field(description="Humidity percentage")
    wind_speed: float = Field(description="Wind speed in kilometers per hour")
    pm25: float = Field(description="Particulate Matter 2.5 micrometers")
    pm10: float = Field(description="Particulate Matter 10 micrometers")
    co: float = Field(description="Carbon Monoxide level")

@dataclass
class UserInput:
    city: str
    state: str
    country: str
    medical_conditions: Optional[str]
    planned_activity: str

class AQIAnalyzer:
    
    def __init__(self, firecrawl_key: str) -> None:
        self.firecrawl = FirecrawlApp(api_key=firecrawl_key)
    
    def _format_url(self, country: str, state: str, city: str) -> str:
        """Format URL based on location, handling cases with and without state"""
        country_clean = country.lower().replace(' ', '-')
        city_clean = city.lower().replace(' ', '-')
        
        if not state or state.lower() == 'none':
            return f"https://www.aqi.in/dashboard/{country_clean}/{city_clean}"
        
        state_clean = state.lower().replace(' ', '-')
        return f"https://www.aqi.in/dashboard/{country_clean}/{state_clean}/{city_clean}"
    
    def fetch_aqi_data(self, city: str, state: str, country: str) -> Dict[str, float]:
        """Fetch AQI data using Firecrawl"""
        try:
            url = self._format_url(country, state, city)
            st.info(f"Accessing URL: {url}")  # Display URL being accessed
            
            response = self.firecrawl.extract(
                urls=[f"{url}/*"],
                params={
                    'prompt': 'Extract the current real-time AQI, temperature, humidity, wind speed, PM2.5, PM10, and CO levels from the page. Also extract the timestamp of the data.',
                    'schema': ExtractSchema.model_json_schema()
                }
            )
            
            aqi_response = AQIResponse(**response)
            if not aqi_response.success:
                raise ValueError(f"Failed to fetch AQI data: {aqi_response.status}")
            
            with st.expander("📦 Raw AQI Data", expanded=False):
                st.json({
                    "url_accessed": url,
                    "timestamp": aqi_response.expiresAt,
                    "data": aqi_response.data
                })
                
                st.warning("""
                    ⚠️ Note: The data shown may not match real-time values on the website. 
                    This could be due to:
                    - Cached data in Firecrawl
                    - Rate limiting
                    - Website updates not being captured
                    
                    Consider refreshing or checking the website directly for real-time values.
                """)
                
            return aqi_response.data
            
        except Exception as e:
            st.error(f"Error fetching AQI data: {str(e)}")
            return {
                'aqi': 0,
                'temperature': 0,
                'humidity': 0,
                'wind_speed': 0,
                'pm25': 0,
                'pm10': 0,
                'co': 0
            }

class HealthRecommendationAgent:
    
    def __init__(self, openai_key: str) -> None:
        self.agent = Agent(
            model=OpenAIChat(
                id="gpt-4o",
                name="Health Recommendation Agent",
                api_key=openai_key
            )
        )
    
    def get_recommendations(
        self,
        aqi_data: Dict[str, float],
        user_input: UserInput
    ) -> str:
        prompt = self._create_prompt(aqi_data, user_input)
        response = self.agent.run(prompt)
        return response.content
    
    def _create_prompt(self, aqi_data: Dict[str, float], user_input: UserInput) -> str:
        return f"""
        Based on the following air quality conditions in {user_input.city}, {user_input.state}, {user_input.country}:
        - Overall AQI: {aqi_data['aqi']}
        - PM2.5 Level: {aqi_data['pm25']} µg/m³
        - PM10 Level: {aqi_data['pm10']} µg/m³
        - CO Level: {aqi_data['co']} ppb
        
        Weather conditions:
        - Temperature: {aqi_data['temperature']}°C
        - Humidity: {aqi_data['humidity']}%
        - Wind Speed: {aqi_data['wind_speed']} km/h
        
        User's Context:
        - Medical Conditions: {user_input.medical_conditions or 'None'}
        - Planned Activity: {user_input.planned_activity}
        **Comprehensive Health Recommendations:**
        1. **Impact of Current Air Quality on Health:**
        2. **Necessary Safety Precautions for Planned Activity:**
        3. **Advisability of Planned Activity:**
        4. **Best Time to Conduct the Activity:**
        """

def analyze_conditions(
    user_input: UserInput,
    api_keys: Dict[str, str]
) -> str:
    aqi_analyzer = AQIAnalyzer(firecrawl_key=api_keys['firecrawl'])
    health_agent = HealthRecommendationAgent(openai_key=api_keys['openai'])
    
    aqi_data = aqi_analyzer.fetch_aqi_data(
        city=user_input.city,
        state=user_input.state,
        country=user_input.country
    )
    
    return health_agent.get_recommendations(aqi_data, user_input)

def initialize_session_state():
    if 'api_keys' not in st.session_state:
        # Get API keys from environment variables
        firecrawl_key = os.environ.get('FIRECRAWL_API_KEY', '')
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        
        st.session_state.api_keys = {
            'firecrawl': firecrawl_key,
            'openai': openai_key
        }
        
        # Check if API keys are available
        if not firecrawl_key:
            st.warning("⚠️ FIRECRAWL_API_KEY not found in environment variables. You can still set it in the sidebar.")
        if not openai_key:
            st.warning("⚠️ OPENAI_API_KEY not found in environment variables. You can still set it in the sidebar.")

def setup_page():
    st.set_page_config(
        page_title="AQI Analysis Agent",
        page_icon="🌍",
        layout="wide"
    )
    
    st.title("🌍 AQI Analysis Agent")
    st.info("Get personalized health recommendations based on air quality conditions.")

def render_sidebar():
    """Render sidebar with API configuration"""
    with st.sidebar:
        st.header("🔑 API Configuration")
        st.info("API keys are loaded from environment variables. You can override them here if needed.")
        
        new_firecrawl_key = st.text_input(
            "Firecrawl API Key",
            type="password",
            value=st.session_state.api_keys['firecrawl'],
            help="Enter your Firecrawl API key or set FIRECRAWL_API_KEY environment variable"
        )
        new_openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_keys['openai'],
            help="Enter your OpenAI API key or set OPENAI_API_KEY environment variable"
        )
        
        if (new_firecrawl_key and new_openai_key and
            (new_firecrawl_key != st.session_state.api_keys['firecrawl'] or 
             new_openai_key != st.session_state.api_keys['openai'])):
            st.session_state.api_keys.update({
                'firecrawl': new_firecrawl_key,
                'openai': new_openai_key
            })
            st.success("✅ API keys updated!")
            
        # Display environment variable setup instructions
        with st.expander("How to set environment variables"):
            st.markdown("""
            ### Setting up environment variables
            
            1. Create a `.env` file in the project root with:
            ```
            FIRECRAWL_API_KEY=your_firecrawl_key_here
            OPENAI_API_KEY=your_openai_key_here
            ```
            
            2. Or set them in your terminal:
            ```bash
            export FIRECRAWL_API_KEY=your_firecrawl_key_here
            export OPENAI_API_KEY=your_openai_key_here
            ```
            """)

def render_main_content():
    st.header("📍 Location Details")
    col1, col2 = st.columns(2)
    
    with col1:
        city = st.text_input("City", placeholder="e.g., Mumbai")
        state = st.text_input("State", placeholder="If it's a Union Territory or a city in the US, leave it blank")
        country = st.text_input("Country", value="India", placeholder="United States")
    
    with col2:
        st.header("👤 Personal Details")
        medical_conditions = st.text_area(
            "Medical Conditions (optional)",
            placeholder="e.g., asthma, allergies"
        )
        planned_activity = st.text_area(
            "Planned Activity",
            placeholder="e.g., morning jog for 2 hours"
        )
    
    return UserInput(
        city=city,
        state=state,
        country=country,
        medical_conditions=medical_conditions,
        planned_activity=planned_activity
    )

def create_aqi_gauge(aqi_value: float) -> go.Figure:
    """Create a gauge chart for AQI value with color zones"""
    
    # Define AQI categories and colors
    categories = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
    colors = ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#99004c', '#7e0023']
    
    # Create thresholds for AQI categories
    thresholds = [0, 50, 100, 150, 200, 300, 500]
    
    # Determine the category based on AQI value
    category_index = 0
    for i, threshold in enumerate(thresholds[1:]):
        if aqi_value <= threshold:
            category_index = i
            break
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=aqi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Air Quality Index<br><span style='font-size:0.8em;color:{colors[category_index]}'>{categories[category_index]}</span>"},
        gauge={
            'axis': {'range': [None, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': colors[category_index]},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#00e400'},
                {'range': [50, 100], 'color': '#ffff00'},
                {'range': [100, 150], 'color': '#ff7e00'},
                {'range': [150, 200], 'color': '#ff0000'},
                {'range': [200, 300], 'color': '#99004c'},
                {'range': [300, 500], 'color': '#7e0023'}
            ],
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig

def create_pollutant_comparison(aqi_data: Dict[str, float]) -> go.Figure:
    """Create a bar chart comparing different pollutants"""
    
    pollutants = ['pm25', 'pm10', 'co']
    values = [aqi_data.get(p, 0) for p in pollutants]
    labels = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'CO (ppb)']
    
    # Define thresholds for each pollutant (simplified)
    thresholds = {
        'pm25': [0, 12, 35.4, 55.4, 150.4, 250.4],  # EPA standards
        'pm10': [0, 54, 154, 254, 354, 424],        # EPA standards
        'co': [0, 4400, 9400, 12400, 15400, 30400]  # Simplified CO thresholds
    }
    
    colors = []
    for i, pollutant in enumerate(pollutants):
        value = values[i]
        thresh = thresholds[pollutant]
        
        if value <= thresh[1]:
            colors.append('#00e400')  # Good
        elif value <= thresh[2]:
            colors.append('#ffff00')  # Moderate
        elif value <= thresh[3]:
            colors.append('#ff7e00')  # Unhealthy for Sensitive Groups
        elif value <= thresh[4]:
            colors.append('#ff0000')  # Unhealthy
        elif value <= thresh[5]:
            colors.append('#99004c')  # Very Unhealthy
        else:
            colors.append('#7e0023')  # Hazardous
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors
        )
    ])
    
    fig.update_layout(
        title="Pollutant Levels",
        xaxis_title="Pollutant Type",
        yaxis_title="Concentration",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig

def create_weather_indicators(aqi_data: Dict[str, float]) -> Dict[str, go.Figure]:
    """Create indicator charts for weather conditions"""
    
    indicators = {}
    
    # Temperature indicator
    temp_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi_data.get('temperature', 0),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Temperature (°C)"},
        gauge={
            'axis': {'range': [-10, 50], 'tickwidth': 1},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [-10, 0], 'color': "#6ECFF6"},
                {'range': [0, 15], 'color': "#85E0F9"},
                {'range': [15, 25], 'color': "#FFFF00"},
                {'range': [25, 35], 'color': "#FFA500"},
                {'range': [35, 50], 'color': "#FF4500"}
            ],
        }
    ))
    temp_fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    indicators['temperature'] = temp_fig
    
    # Humidity indicator
    humidity_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi_data.get('humidity', 0),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Humidity (%)"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [0, 30], 'color': "#FFFACD"},
                {'range': [30, 60], 'color': "#87CEEB"},
                {'range': [60, 100], 'color': "#1E90FF"}
            ],
        }
    ))
    humidity_fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    indicators['humidity'] = humidity_fig
    
    # Wind speed indicator
    wind_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi_data.get('wind_speed', 0),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Wind Speed (km/h)"},
        gauge={
            'axis': {'range': [0, 50], 'tickwidth': 1},
            'bar': {'color': "lightblue"},
            'steps': [
                {'range': [0, 5], 'color': "#E0FFFF"},
                {'range': [5, 20], 'color': "#87CEEB"},
                {'range': [20, 35], 'color': "#4682B4"},
                {'range': [35, 50], 'color': "#000080"}
            ],
        }
    ))
    wind_fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    indicators['wind_speed'] = wind_fig
    
    return indicators

def render_aqi_dashboard(aqi_data: Dict[str, float], user_input: UserInput):
    """Render a dashboard with AQI and weather visualizations"""
    
    st.header("📊 Air Quality Dashboard")
    
    # Display location and timestamp
    st.subheader(f"📍 {user_input.city}, {user_input.state or ''} {user_input.country}")
    st.caption(f"Data as of: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Main AQI gauge
    st.plotly_chart(create_aqi_gauge(aqi_data.get('aqi', 0)), use_container_width=True)
    
    # Pollutant comparison
    st.subheader("🔬 Pollutant Levels")
    st.plotly_chart(create_pollutant_comparison(aqi_data), use_container_width=True)
    
    # Weather indicators
    st.subheader("🌤️ Weather Conditions")
    weather_indicators = create_weather_indicators(aqi_data)
    
    cols = st.columns(3)
    with cols[0]:
        st.plotly_chart(weather_indicators['temperature'], use_container_width=True)
    with cols[1]:
        st.plotly_chart(weather_indicators['humidity'], use_container_width=True)
    with cols[2]:
        st.plotly_chart(weather_indicators['wind_speed'], use_container_width=True)
    
    # Health impact summary
    st.subheader("🩺 Health Impact Summary")
    
    aqi_value = aqi_data.get('aqi', 0)
    if aqi_value <= 50:
        impact = "Good air quality with minimal health concerns."
        color = "#00e400"
    elif aqi_value <= 100:
        impact = "Moderate air quality. Unusually sensitive individuals should consider limiting prolonged outdoor exertion."
        color = "#ffff00"
    elif aqi_value <= 150:
        impact = "Unhealthy for sensitive groups. People with respiratory or heart disease, the elderly and children should limit prolonged outdoor exertion."
        color = "#ff7e00"
    elif aqi_value <= 200:
        impact = "Unhealthy. Everyone may begin to experience health effects. Sensitive groups should limit outdoor exertion."
        color = "#ff0000"
    elif aqi_value <= 300:
        impact = "Very Unhealthy. Health warnings of emergency conditions. The entire population is more likely to be affected."
        color = "#99004c"
    else:
        impact = "Hazardous. Health alert: everyone may experience more serious health effects."
        color = "#7e0023"
    
    st.markdown(f"<div style='background-color:{color}20; padding:10px; border-radius:5px; border-left:5px solid {color};'>{impact}</div>", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    initialize_session_state()
    setup_page()
    render_sidebar()
    user_input = render_main_content()
    
    result = None
    aqi_data = None
    
    if st.button("🔍 Analyze & Get Recommendations"):
        if not all([user_input.city, user_input.planned_activity]):
            st.error("Please fill in all required fields (state and medical conditions are optional)")
        elif not all(st.session_state.api_keys.values()):
            st.error("Please provide both API keys in the sidebar")
        else:
            try:
                with st.spinner("🔄 Analyzing conditions..."):
                    # First fetch AQI data
                    aqi_analyzer = AQIAnalyzer(firecrawl_key=st.session_state.api_keys['firecrawl'])
                    aqi_data = aqi_analyzer.fetch_aqi_data(
                        city=user_input.city,
                        state=user_input.state,
                        country=user_input.country
                    )
                    
                    # Then get recommendations
                    health_agent = HealthRecommendationAgent(openai_key=st.session_state.api_keys['openai'])
                    result = health_agent.get_recommendations(aqi_data, user_input)
                    
                    st.success("✅ Analysis completed!")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    if aqi_data:
        # Render the AQI dashboard with visualizations
        render_aqi_dashboard(aqi_data, user_input)
        
    if result:
        st.markdown("### 📦 Recommendations")
        st.markdown(result)
        
        st.download_button(
            "💾 Download Recommendations",
            data=result,
            file_name=f"aqi_recommendations_{user_input.city}_{user_input.state}.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()