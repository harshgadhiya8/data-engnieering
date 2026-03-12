import requests
import json
import pandas as pd

url = "https://api.open-meteo.com/v1/forecast"

dict = {
    "London, UK": [51.5074, -0.1278],
    "New York, USA": [40.7128, -74.0060],
    "Tokyo, Japan": [35.6895, 139.6917],
    "Mumbai, India": [19.0760, 72.8777],
    "Sydney, Australia": [-33.8688, 151.2093]
}
weather_data = []
for city, coords in dict.items():
    params = {
        "latitude": coords[0],
        "longitude": coords[1],
        "current_weather": True
    }
    response = requests.get(url, params=params)
    data = response.json()
    weather_data.append({
        "city": city,
        "temperature": data["current_weather"]["temperature"],
        "windspeed": data["current_weather"]["windspeed"],
        "winddirection": data["current_weather"]["winddirection"],
        "weathercode": data["current_weather"]["weathercode"],
        "time": data["current_weather"]["time"]
    })

df = pd.DataFrame(weather_data)
df.columns = ["city", "temperature_celsius", "wind_speed_kmh", "wind_direction_degrees", "weather_code", "time"]
df.status = df.apply(lambda x: "Hot" if x["temperature_celsius"] > 25 else "Cold")
print(df)