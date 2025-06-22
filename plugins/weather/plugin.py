"""
Weather Tool Plugin for Atlas

This plugin provides weather information and forecasts for any location.
"""

import json
import logging
import requests
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class WeatherPlugin:
    """Weather information plugin for Atlas."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.api_key = self.config.get("api_key", "")
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def initialize(self, llm_manager=None, atlas_app=None, agent_manager=None) -> bool:
        """Initialize the plugin."""
        try:
            logger.info("Weather plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize weather plugin: {e}")
            return False
    
    def get_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location."""
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Weather API key not configured"
                }
            
            # Get coordinates for location
            geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            
            response = requests.get(geocode_url, params=params)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get location coordinates: {response.status_code}"
                }
            
            geocode_data = response.json()
            if not geocode_data:
                return {
                    "success": False,
                    "error": f"Location '{location}' not found"
                }
            
            lat = geocode_data[0]["lat"]
            lon = geocode_data[0]["lon"]
            
            # Get weather data
            weather_url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(weather_url, params=params)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get weather data: {response.status_code}"
                }
            
            weather_data = response.json()
            
            return {
                "success": True,
                "data": {
                    "location": location,
                    "temperature": weather_data["main"]["temp"],
                    "feels_like": weather_data["main"]["feels_like"],
                    "humidity": weather_data["main"]["humidity"],
                    "pressure": weather_data["main"]["pressure"],
                    "description": weather_data["weather"][0]["description"],
                    "wind_speed": weather_data["wind"]["speed"],
                    "wind_direction": weather_data["wind"].get("deg", 0)
                },
                "message": f"Current weather for {location}"
            }
            
        except Exception as e:
            logger.error(f"Weather lookup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a location."""
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Weather API key not configured"
                }
            
            # Get coordinates for location
            geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            
            response = requests.get(geocode_url, params=params)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get location coordinates: {response.status_code}"
                }
            
            geocode_data = response.json()
            if not geocode_data:
                return {
                    "success": False,
                    "error": f"Location '{location}' not found"
                }
            
            lat = geocode_data[0]["lat"]
            lon = geocode_data[0]["lon"]
            
            # Get forecast data
            forecast_url = f"{self.base_url}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(forecast_url, params=params)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get forecast data: {response.status_code}"
                }
            
            forecast_data = response.json()
            
            # Process forecast data
            daily_forecasts = []
            current_date = None
            daily_data = {}
            
            for item in forecast_data["list"]:
                date = item["dt_txt"].split(" ")[0]
                if date != current_date:
                    if current_date and daily_data:
                        daily_forecasts.append(daily_data)
                    current_date = date
                    daily_data = {
                        "date": date,
                        "temp_min": item["main"]["temp_min"],
                        "temp_max": item["main"]["temp_max"],
                        "description": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"]
                    }
                else:
                    # Update min/max temperatures
                    daily_data["temp_min"] = min(daily_data["temp_min"], item["main"]["temp_min"])
                    daily_data["temp_max"] = max(daily_data["temp_max"], item["main"]["temp_max"])
            
            if daily_data:
                daily_forecasts.append(daily_data)
            
            # Limit to requested days
            daily_forecasts = daily_forecasts[:days]
            
            return {
                "success": True,
                "data": {
                    "location": location,
                    "forecast": daily_forecasts,
                    "days": len(daily_forecasts)
                },
                "message": f"{days}-day forecast for {location}"
            }
            
        except Exception as e:
            logger.error(f"Forecast lookup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_location_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get weather for specific coordinates."""
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Weather API key not configured"
                }
            
            # Get weather data
            weather_url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(weather_url, params=params)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get weather data: {response.status_code}"
                }
            
            weather_data = response.json()
            
            return {
                "success": True,
                "data": {
                    "coordinates": {"lat": lat, "lon": lon},
                    "temperature": weather_data["main"]["temp"],
                    "feels_like": weather_data["main"]["feels_like"],
                    "humidity": weather_data["main"]["humidity"],
                    "pressure": weather_data["main"]["pressure"],
                    "description": weather_data["weather"][0]["description"],
                    "wind_speed": weather_data["wind"]["speed"],
                    "wind_direction": weather_data["wind"].get("deg", 0)
                },
                "message": f"Weather at coordinates ({lat}, {lon})"
            }
            
        except Exception as e:
            logger.error(f"Location weather lookup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def register(llm_manager=None, atlas_app=None, agent_manager=None):
    """Register the Weather plugin."""
    plugin = WeatherPlugin()
    if plugin.initialize(llm_manager, atlas_app, agent_manager):
        return {
            "tools": [
                plugin.get_weather,
                plugin.get_forecast,
                plugin.get_location_weather
            ],
            "agents": []
        }
    else:
        logger.warning("Weather plugin initialization failed")
        return {"tools": [], "agents": []} 