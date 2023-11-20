import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
from collections import defaultdict
from shapely.geometry import Polygon, Point
import itertools
import geopy.distance

# Load environment variables from a .env file
load_dotenv()

# Connect to MongoDB client
client = MongoClient("localhost:27017")

# Access the specified database and collection
db = client["Ironhack"]
c = db.get_collection("companies")

# Function to find the top 3 cities with the most gaming companies
def find_top_3_gaming_cities():
    """
    Retrieves and counts the number of gaming companies in each city,
    returning the top 3 cities with the highest counts.
    Returns:
    - DataFrame with the top 3 cities and their respective counts.
    """
    # MongoDB query filter for gaming companies
    filter_1 = {
        "tag_list": {"$regex": "gaming", "$options": "i"}
    }

    # Projection to retrieve only city information
    projection = {"_id": 0, "offices.city": 1}

    # Execute the query
    query = list(c.find(filter_1, projection).sort("name", -1))

    # Count the occurrences of each city
    city_counts = defaultdict(int)
    for item in query:
        for office in item['offices']:
            city = office.get('city', '')
            if city:  # Exclude empty city entries
                city_counts[city] += 1

    # Sort cities by count in descending order and extract top 3
    sorted_city_counts = {k: v for k, v in sorted(city_counts.items(), key=lambda item: item[1], reverse=True)}
    top_10_cities = dict(list(sorted_city_counts.items())[:3])

    return pd.DataFrame(list(top_10_cities.items()), columns=['City', 'Count'])

# Function to retrieve location data of top 3 gaming cities
def top_3_cities_location():
    """
    Retrieves the location data (latitude and longitude) of gaming companies in the top 3 gaming cities.
    Returns:
    - DataFrame with the company names, cities, and their location data.
    """
    # Filters for gaming companies in the top 3 cities
    filter_1 = {
        "tag_list": {"$regex": "gaming", "$options": "i"},
    }
    filter_2 = {
        "offices": {"$elemMatch": {"city": "San Francisco"}},
    }
    filter_3 = {
        "offices": {"$elemMatch": {"city": "New York"}},
    }
    filter_4 = {
        "offices": {"$elemMatch": {"city": "London"}},
    }

    # Projection to retrieve relevant fields
    projection = {"_id": 0, "name": 1, "offices.address1": 1, "offices.city": 1, "offices.latitude": 1, "offices.longitude": 1}

    # Execute the query
    query_top_3_gaming = list(c.find({"$and": [filter_1, {"$or": [filter_2, filter_3, filter_4]}]}, projection))

    # Flatten the data for ease of analysis
    flattened_data = []
    for company in query_top_3_gaming:
        for office in company['offices']:
            flattened_data.append({
                'Company Name': company['name'],
                'City': office['city'],
                'Street': office['address1'],
                'Latitude': office['latitude'],
                'Longitude': office['longitude']
            })

    # Convert to DataFrame, remove duplicates and NaN values
    df = pd.DataFrame(flattened_data).drop_duplicates().dropna(subset=['Latitude', 'Longitude'])

    # Filter for the top 3 gaming cities
    cities_to_include = ['San Francisco', 'New York', 'London']
    df_filtered_top_3 = df[df['City'].isin(cities_to_include)].sort_values(by="City")

    return df_filtered_top_3

"""
def get_city_midpoint(df, city_name):
    
    Calculates the midpoint for a specified city based on the two farthest points within a threshold distance.
    Args:
    - df: DataFrame containing the data.
    - city_name: Name of the city.
    Returns:
    - Tuple containing the latitude and longitude of the midpoint.
    

    # Filter DataFrame for entries corresponding to the specified city
    city_df = df[df['City'] == city_name]

    # Return None if there is no data for the city
    if city_df.empty:
        print(f"No data available for {city_name}.")
        return None

    # Initialize initial centroid
    initial_centroid = Point(city_df['Longitude'].mean(), city_df['Latitude'].mean())

    # Set threshold for maximum allowable distance from initial centroid (for filtering outliers)
    threshold_distance = 0.05  # Equivalent to approximately 5 km

    # Exclude points beyond the threshold distance from initial centroid
    filtered_df = city_df[city_df.apply(lambda row: Point(row['Longitude'], row['Latitude']).distance(initial_centroid) < threshold_distance, axis=1)]

    # Identify two points in the filtered dataset that are farthest from each other
    max_distance = 0
    point1, point2 = None, None
    for (lat1, lon1), (lat2, lon2) in itertools.combinations(filtered_df[['Latitude', 'Longitude']].values, 2):
        distance = Point(lon1, lat1).distance(Point(lon2, lat2))
        if distance > max_distance:
            max_distance, point1, point2 = distance, (lat1, lon1), (lat2, lon2)

    # Compute midpoint of the two farthest points
    midpoint_lat = (point1[0] + point2[0]) / 2
    midpoint_lon = (point1[1] + point2[1]) / 2

    return midpoint_lat, midpoint_lon

"""

def get_city_midpoint_and_radius(df, city_name):
    """
    Calculates the midpoint and radius for a specified city based on the two farthest points within a threshold distance.
    Args:
    - df: DataFrame containing the data.
    - city_name: Name of the city.
    Returns:
    - Tuple containing the latitude and longitude of the midpoint and the radius in meters.
    """

    # Filter DataFrame for entries corresponding to the specified city
    city_df = df[df['City'] == city_name]

    # Return None if there is no data for the city
    if city_df.empty:
        print(f"No data available for {city_name}.")
        return None, None

    # Initialize initial centroid
    initial_centroid = Point(city_df['Longitude'].mean(), city_df['Latitude'].mean())

    # Set threshold for maximum allowable distance from initial centroid (for filtering outliers)
    threshold_distance = 0.05  # Equivalent to approximately 5 km

    # Exclude points beyond the threshold distance from initial centroid
    filtered_df = city_df[city_df.apply(lambda row: Point(row['Longitude'], row['Latitude']).distance(initial_centroid) < threshold_distance, axis=1)]

    # Identify two points in the filtered dataset that are farthest from each other
    max_distance = 0
    point1, point2 = None, None
    for (lat1, lon1), (lat2, lon2) in itertools.combinations(filtered_df[['Latitude', 'Longitude']].values, 2):
        distance = geopy.distance.distance((lat1, lon1), (lat2, lon2)).meters
        if distance > max_distance:
            max_distance, point1, point2 = distance, (lat1, lon1), (lat2, lon2)

    # Compute midpoint of the two farthest points
    midpoint_lat = (point1[0] + point2[0]) / 2
    midpoint_lon = (point1[1] + point2[1]) / 2

    # The radius is half the distance between the two farthest points
    radius = max_distance / 2

    return (midpoint_lat, midpoint_lon, radius)

df = top_3_cities_location()

def midpoint_coordinates_radius_sf():
    """
    Retrieves the latitude and longitude of the midpoint for San Francisco.
    Returns:
    - Tuple containing the latitude and longitude of the midpoint.
    """
    # Call get_city_midpoint to compute the midpoint for San Francisco
    sflat, sflon, radius = get_city_midpoint_and_radius(df, "San Francisco")

    # Return the computed midpoint coordinates
    return sflat, sflon, radius


def midpoint_coordinates_radius_ny():
    """
    Retrieves the latitude and longitude of the midpoint for New York.
    Returns:
    - Tuple containing the latitude and longitude of the midpoint.
    """
    # Call get_city_midpoint to compute the midpoint for New York
    nylat, nylon, radius = get_city_midpoint_and_radius(df, "New York")
    
    # Return the computed midpoint coordinates
    return nylat, nylon, radius

def midpoint_coordinates_radius_ldn():
    """
    Retrieves the latitude and longitude of the midpoint for London.
    Returns:
    - Tuple containing the latitude and longitude of the midpoint.
    """
    # Call get_city_midpoint to compute the midpoint for London
    ldnlat, ldnlon, radius = get_city_midpoint_and_radius(df, "London")

    # Return the computed midpoint coordinates
    return ldnlat, ldnlon, radius