from flask import Flask, render_template, request, jsonify
import requests
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from flask_caching import Cache

app = Flask(__name__)

# Configure caching to store past temperatures
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Store past temperatures
temperature_data = {}

API_KEY = "d171b37995fa8f1e93ba45b009b93f37"  # Replace with your OpenWeatherMap API key

def fetch_weather(city):
    """Fetch weather data from OpenWeather API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        return temp
    else:
        return None

def generate_plot(city):
    """Generate temperature trend graph"""
    plt.figure(figsize=(6, 4))
    
    # Get stored temperature data
    times = list(temperature_data[city].keys())
    temps = list(temperature_data[city].values())

    # Plot temperature trend
    plt.plot(times, temps, marker='o', linestyle='-', color='b', label="Past Temperatures")

    # Mark latest temperature
    if temps:
        plt.axhline(y=temps[-1], color='r', linestyle='dashed', label=f"Current Temp: {temps[-1]}°C")

    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.title(f"Temperature Trend for {city}")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()

    # Save the plot as base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return graph_url

@app.route("/", methods=["GET", "POST"])
def home():
    temp, graph = None, None
    if request.method == "POST":
        city = request.form["city"].strip().lower()
        
        if city:
            temp = fetch_weather(city)
            
            if temp is not None:
                # Store temperature with timestamp
                if city not in temperature_data:
                    temperature_data[city] = {}
                temperature_data[city][datetime.now().strftime("%H:%M:%S")] = temp

                graph = generate_plot(city)
            else:
                return render_template("index.html", error="City not found or API issue.")

    return render_template("index.html", temp=temp, graph=graph)

if __name__ == "__main__":
    app.run(debug=True)

