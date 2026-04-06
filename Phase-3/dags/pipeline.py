import requests
import json
import pandas as pd
from sqlalchemy import create_engine
import logging
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log")
    ]
)

def extract():
    url = "https://api.open-meteo.com/v1/forecast"
    cities = {
        "London, UK": [51.5074, -0.1278],
        "New York, USA": [40.7128, -74.0060],
        "Tokyo, Japan": [35.6895, 139.6917],
        "Mumbai, India": [19.0760, 72.8777],
        "Sydney, Australia": [-33.8688, 151.2093]
    }
    weather_data = []
    for city, coords in cities.items():
        params = {
            "latitude": coords[0],
            "longitude": coords[1],
            "current_weather": True
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
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

    # Save raw data as JSON file
    with open("raw_weather.json", "w") as f:
        json.dump(weather_data, f)
    logging.info("Raw data saved to raw_weather.json")


def transform():
    # Read from JSON file that extract() saved
    with open("raw_weather.json", "r") as f:
        weather_data = json.load(f)

    df = pd.DataFrame(weather_data)
    df.columns = ["city", "temperature_celsius", "wind_speed_kmh", 
                  "wind_direction_degrees", "weather_code", "time"]
    df["status"] = df.apply(
        lambda x: "Hot" if x["temperature_celsius"] > 25 else "Cold", axis=1
    )
    logging.info("Transformation complete")

    # Save as Parquet file
    df.to_parquet("weather_data.parquet", index=False)
    logging.info("Data saved to weather_data.parquet")


def load():
    # Read from Parquet file that transform() saved
    df = pd.read_parquet("weather_data.parquet")

    try:
        engine = create_engine("postgresql://harsh:@localhost:5432/postgres")
        df.to_sql("weather", engine, if_exists="append", index=False)
        logging.info("Data successfully loaded into PostgreSQL")
    except Exception as e:
        logging.error(f"Failed to load data into PostgreSQL: {e}")


def dbt_run():
    try:
        result = subprocess.run(
            ["dbt", "run"],
            cwd="/Users/harsh/data-engineering/Phase-2/ecommerce",  
            capture_output=True
        )
        logging.info(result.stdout.decode())
        if result.returncode != 0:
            logging.error(result.stderr.decode())
            raise Exception("dbt run failed")
        logging.info("dbt models ran successfully")
    except Exception as e:
        logging.error(f"dbt run failed: {e}")


# This runs the pipeline when you execute the script directly
if __name__ == "__main__":
    extract()
    transform()
    load()
    dbt_run()