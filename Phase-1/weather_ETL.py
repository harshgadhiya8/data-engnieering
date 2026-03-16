import requests
import json
import pandas as pd
from sqlalchemy import create_engine
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),             # prints to terminal
        logging.FileHandler("pipeline.log")  # saves to a file
    ]
)
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
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        weather_data.append({
            "city": city,
            "temperature": data["current_weather"]["temperature"],
            "windspeed": data["current_weather"]["windspeed"],
            "winddirection": data["current_weather"]["winddirection"],
            "weathercode": data["current_weather"]["weathercode"],
            "time": data["current_weather"]["time"]
        })
        logging.info(f"Successfully fetched weather data for {city}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch weather data for {city}: {e}")
    

df = pd.DataFrame(weather_data)
df.columns = ["city", "temperature_celsius", "wind_speed_kmh", "wind_direction_degrees", "weather_code", "time"]
df["status"] = df.apply(lambda x: "Hot" if x["temperature_celsius"] > 25 else "Cold", axis=1)
print(df)
df.to_parquet("weather_data.parquet", index=False)
try:
    engine = create_engine("postgresql://harsh:@localhost:5432/postgres")
    df.to_sql("weather", engine, if_exists="append", index=False)
    logging.info("Data successfully loaded into SQL database")
except Exception as e:
    logging.error(f"Failed to load data into SQL database: {e}")
