import requests
from datetime import datetime, timedelta
import google.generativeai as genai
import os
from dotenv import load_dotenv
from database import weather_db
import json
import logging

load_dotenv()

class WeatherService:
    def __init__(self):
        """Initialize weather service with OpenWeatherMap API and Gemini AI"""
        # Get API keys
        self.openweather_api_key = os.getenv('OPEN_WEATHER_API')
        self.base_url = "https://api.openweathermap.org/data/2.5"

        # Initialize Gemini AI
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.genai_model = None

    def get_coordinates(self, location_name):
        """Get coordinates for a location name (simplified - you might want to use a geocoding service)"""
        # Common South African farming locations
        locations = {
            'cape town': (-33.9221, 18.4231),
            'johannesburg': (-26.2041, 28.0473),
            'durban': (-29.8587, 31.0218),
            'pretoria': (-25.7479, 28.2293),
            'bloemfontein': (-29.0852, 26.1596),
            'port elizabeth': (-33.9608, 25.6022),
            'kimberley': (-28.7282, 24.7499),
            'polokwane': (-23.9045, 29.4689),
            'nelspruit': (-25.4753, 30.9694),
            'upington': (-28.4478, 21.2561)
        }

        location_lower = location_name.lower()
        return locations.get(location_lower, (-33.9221, 18.4231))  # Default to Cape Town

    def is_weather_data_fresh(self, location):
        """Check if we have fresh weather data for today"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            cached_data = weather_db.get_weather_for_date(location, today)
            return cached_data is not None
        except Exception as e:
            print(f"Error checking cached weather data: {e}")
            return False

    def get_current_weather(self, location):
        """Get current weather data for a location with intelligent caching"""
        # Check if we have fresh data for today
        if self.is_weather_data_fresh(location):
            print(f"Using cached weather data for {location}")
            today = datetime.now().strftime('%Y-%m-%d')
            cached_data = weather_db.get_weather_for_date(location, today)
            return cached_data['weather_data']

        # Fetch fresh data from OpenWeatherMap
        print(f"Fetching fresh weather data for {location} from OpenWeatherMap")

        if not self.openweather_api_key:
            print("OpenWeatherMap API key not found")
            return None

        try:
            lat, lon = self.get_coordinates(location)

            # Get current weather
            current_url = f"{self.base_url}/weather"
            current_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.openweather_api_key,
                "units": "metric"
            }

            current_response = requests.get(current_url, params=current_params)
            current_response.raise_for_status()
            current_data = current_response.json()

            # Get 5-day forecast
            forecast_url = f"{self.base_url}/forecast"
            forecast_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.openweather_api_key,
                "units": "metric"
            }

            forecast_response = requests.get(forecast_url, params=forecast_params)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Process current weather
            current_weather = {
                "temperature": float(round(current_data["main"]["temp"], 1)),
                "humidity": float(round(current_data["main"]["humidity"], 1)),
                "precipitation": 0.0,  # Current precipitation not available in free tier
                "weather_code": int(current_data["weather"][0]["id"]),
                "weather_description": str(current_data["weather"][0]["description"]),
                "wind_speed": float(round(current_data["wind"]["speed"] * 3.6, 1)),  # Convert m/s to km/h
                "wind_direction": float(current_data["wind"].get("deg", 0)),
                "pressure": float(current_data["main"]["pressure"]),
                "feels_like": float(round(current_data["main"]["feels_like"], 1)),
                "timestamp": datetime.now().isoformat()
            }

            # Process daily forecast (group by day)
            daily_data = []
            daily_groups = {}

            for item in forecast_data["list"]:
                date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                if date not in daily_groups:
                    daily_groups[date] = []
                daily_groups[date].append(item)

            for date, day_items in list(daily_groups.items())[:7]:  # Limit to 7 days
                temps = [item["main"]["temp"] for item in day_items]
                precipitation = sum([item.get("rain", {}).get("3h", 0) + item.get("snow", {}).get("3h", 0) for item in day_items])
                wind_speeds = [item["wind"]["speed"] * 3.6 for item in day_items]  # Convert to km/h

                daily_data.append({
                    "date": str(date),
                    "temp_max": float(round(max(temps), 1)),
                    "temp_min": float(round(min(temps), 1)),
                    "precipitation": float(round(precipitation, 2)),
                    "weather_code": int(day_items[0]["weather"][0]["id"]),
                    "weather_description": str(day_items[0]["weather"][0]["description"]),
                    "wind_speed_max": float(round(max(wind_speeds), 1))
                })

            weather_data = {
                "location": str(location),
                "coordinates": {"lat": float(lat), "lon": float(lon)},
                "current": current_weather,
                "daily_forecast": daily_data,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "timezone": int(current_data.get("timezone", 0)),
                "api_calls_saved": "Using database caching to minimize API usage"
            }

            # Save to database for future use
            weather_db.save_weather_data(location, weather_data)
            print(f"Weather data cached for {location}")

            return weather_data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data from OpenWeatherMap: {e}")
            return None
        except Exception as e:
            print(f"Error processing weather data: {e}")
            return None

    def get_farming_weather_analysis(self, location, crop_type="maize"):
        """Get AI-powered farming weather analysis"""
        weather_data = self.get_current_weather(location)

        if not weather_data or not self.genai_model:
            return "Weather analysis unavailable"

        prompt = f"""
        As an agricultural weather expert, analyze the following weather data for {crop_type} farming in {location}:

        Current Weather:
        - Temperature: {weather_data['current']['temperature']}°C
        - Humidity: {weather_data['current']['humidity']}%
        - Precipitation: {weather_data['current']['precipitation']}mm
        - Wind Speed: {weather_data['current']['wind_speed']} km/h

        7-Day Forecast:
        """

        for day in weather_data['daily_forecast']:
            prompt += f"\n- {day['date']}: {day['temp_min']}-{day['temp_max']}°C, Precipitation: {day['precipitation']}mm"

        prompt += f"""

        Please provide:
        1. Current weather impact on {crop_type} growth
        2. Recommendations for the next 7 days
        3. Irrigation needs based on precipitation forecast
        4. Any weather-related risks or opportunities
        5. Optimal farming activities for this weather pattern

        Keep the response practical and actionable for farmers.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate weather analysis: {str(e)}"

    def get_weather_alerts(self, location, crop_type="maize"):
        """Get weather alerts and warnings for farming"""
        weather_data = self.get_current_weather(location)

        if not weather_data:
            return []

        alerts = []
        current = weather_data['current']
        forecast = weather_data['daily_forecast']

        # Temperature alerts
        if current['temperature'] > 35:
            alerts.append({
                "type": "heat_warning",
                "message": f"High temperature alert: {current['temperature']}°C. Consider additional irrigation.",
                "severity": "high"
            })
        elif current['temperature'] < 5:
            alerts.append({
                "type": "frost_warning",
                "message": f"Frost risk: {current['temperature']}°C. Protect sensitive crops.",
                "severity": "high"
            })

        # Precipitation alerts
        total_precipitation = sum([day['precipitation'] for day in forecast[:3]])
        if total_precipitation > 50:
            alerts.append({
                "type": "heavy_rain",
                "message": f"Heavy rain expected: {total_precipitation}mm over next 3 days. Check drainage.",
                "severity": "medium"
            })
        elif total_precipitation < 5:
            alerts.append({
                "type": "drought_risk",
                "message": "Low precipitation forecast. Plan irrigation schedule.",
                "severity": "medium"
            })

        # Wind alerts
        if current['wind_speed'] > 30:
            alerts.append({
                "type": "high_wind",
                "message": f"High wind speed: {current['wind_speed']} km/h. Secure equipment and check for crop damage.",
                "severity": "medium"
            })

        return alerts

# Initialize weather service
weather_service = WeatherService()