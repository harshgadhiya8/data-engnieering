# Start from official Python 3.12 image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file into container
COPY requirements.txt .

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your ETL script into container
COPY weather_ETL.py .

# Command to run when container starts
CMD ["python", "weather_ETL.py"]