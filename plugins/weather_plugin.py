from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout
import requests
from plugins.base import PluginBase

class WeatherPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.city = "Kyiv"
        self.last_weather = None

    def get_widget(self, parent=None):
        w = QWidget(parent)
        layout = QVBoxLayout(w)
        self.weather_label = QLabel("Weather: ?")
        self.weather_label.setStyleSheet("color: #00fff7; font-size: 15px;")
        layout.addWidget(self.weather_label)
        btn = QPushButton("Get Weather")
        btn.setStyleSheet("background: #00fff7; color: #181c20; border-radius: 6px; padding: 4px 12px;")
        btn.clicked.connect(self.update_weather)
        layout.addWidget(btn)
        return w

    def get_settings(self):
        return {"city": self.city}

    def set_settings(self, settings):
        self.city = settings.get("city", self.city)

    def settings_widget(self, parent=None):
        w = QWidget(parent)
        layout = QHBoxLayout(w)
        label = QLabel("City:")
        edit = QLineEdit(self.city)
        edit.setPlaceholderText("Enter city...")
        def on_edit():
            self.city = edit.text()
        edit.editingFinished.connect(on_edit)
        layout.addWidget(label)
        layout.addWidget(edit)
        return w

    def update_weather(self):
        city = self.city
        try:
            # Get coordinates from Open-Meteo geocoding
            geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
            if not geo.get("results"):
                self.weather_label.setText("Weather: city not found")
                return
            lat = geo["results"][0]["latitude"]
            lon = geo["results"][0]["longitude"]
            # Get weather
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            data = requests.get(url).json()
            weather = data.get("current_weather", {})
            temp = weather.get("temperature")
            wind = weather.get("windspeed")
            text = f"Weather in {city}: {temp}°C, wind {wind} km/h"
            self.weather_label.setText(text)
            self.last_weather = text
        except Exception as e:
            self.weather_label.setText(f"Weather: error {e}")

    def info(self):
        return {
            "name": "WeatherPlugin",
            "description": "Shows current weather for a city using open-meteo.com API.",
            "active": self.active
        } 