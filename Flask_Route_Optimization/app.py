import urllib.parse
import requests
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request

# Constants for fuel efficiency (kg CO2 per liter of fuel burned)
CO2_PER_LITER_CAR = 2.31  # Average CO2 emission per liter of gasoline for cars
CO2_PER_LITER_TRUCK = 2.68  # Average CO2 emission per liter of diesel for trucks in India

# Initialize Flask app
app = Flask(__name__)

# Function to get coordinates of a location
def get_coordinates(location):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(location)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

# Function to get distance between start and destination coordinates using OSRM
def get_osrm_distance(start_location, destination):
    """
    Use OSRM to get the estimated distance (in km) for the journey.
    """
    start_coords = start_location  # Example: (lat, lon)
    destination_coords = destination  # Example: (lat, lon)

    # OSRM API URL for route calculation
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{destination_coords[1]},{destination_coords[0]}?overview=false"

    # Make the API request
    response = requests.get(url)
    data = response.json()
    
    if data['routes']:
        distance_meters = data['routes'][0]['legs'][0]['distance']
        distance_km = distance_meters / 1000  # Convert meters to kilometers
        return round(distance_km, 2)  # Round to two decimal places
    else:
        print("Error: Unable to fetch route data from OSRM.")
        return None

# Function to calculate fuel consumption
def calculate_fuel_consumption(distance_km, mileage_kmpl):
    """
    Calculate fuel consumption based on distance and mileage.
    Returns fuel consumption in liters.
    """
    return distance_km / mileage_kmpl

# Function to calculate CO2 emission
def calculate_carbon_emission(fuel_consumption_liters, vehicle_type):
    """
    Calculate the CO2 emissions from fuel consumption (in liters).
    Returns the CO2 emission in kg.
    """
    if vehicle_type == 'car':
        return fuel_consumption_liters * CO2_PER_LITER_CAR
    elif vehicle_type == 'truck':
        return fuel_consumption_liters * CO2_PER_LITER_TRUCK

# Function to generate Google Maps URL
def generate_google_maps_url(start_location, destination):
    """
    Generate the Google Maps URL for the given start and destination locations.
    """
    base_url = "https://www.google.com/maps/dir/"
    return f"{base_url}{start_location}/{destination}"

# Function to provide travel insights
def provide_travel_insights(start_location, destination, mileage, distance_km, vehicle_type):
    """
    Provide unique travel insights based on user inputs, fuel consumption, and CO2 emission calculations.
    """
    # Fuel consumption and carbon emission calculations
    fuel_consumption = calculate_fuel_consumption(distance_km, mileage)
    carbon_emission = calculate_carbon_emission(fuel_consumption, vehicle_type)
    
    # Eco-Friendly Tip Impact (e.g., reduced stops reduce fuel consumption)
    eco_fuel_savings = fuel_consumption * 0.10  # Assume 10% fuel saving from eco-friendly tip
    eco_carbon_savings = eco_fuel_savings * (CO2_PER_LITER_CAR if vehicle_type == 'car' else CO2_PER_LITER_TRUCK)

    # Return the insights as a dictionary
    insights = {
        'start_location': urllib.parse.unquote(start_location),
        'destination': urllib.parse.unquote(destination),
        'fuel_consumption': round(fuel_consumption, 2),
        'carbon_emission': round(carbon_emission, 2),
        'eco_fuel_savings': round(eco_fuel_savings, 2),
        'eco_carbon_savings': round(eco_carbon_savings, 2),
    }
    
    return insights

# Flask route to handle the user input and process the data
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get inputs from the form
        start_location = request.form['start_location']
        destination = request.form['destination']
        mileage = float(request.form['mileage'])
        vehicle_type = request.form['vehicle_type']

        # Get coordinates for start and destination locations
        start_coords = get_coordinates(start_location)
        dest_coords = get_coordinates(destination)

        # Check if coordinates are valid
        if not start_coords or not dest_coords:
            return "Could not find coordinates for the given locations."

        # Calculate distance using OSRM API
        distance_km = get_osrm_distance(start_coords, dest_coords)
        if distance_km is None:
            return "Error calculating distance."

        # Provide travel insights
        insights = provide_travel_insights(start_location, destination, mileage, distance_km, vehicle_type)

        # Generate Google Maps URL
        google_maps_url = generate_google_maps_url(start_location, destination)

        # Render the result page with insights and the Google Maps link
        return render_template('result.html', insights=insights, google_maps_url=google_maps_url)

    return render_template('index.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
