from . import gaming_companies

import pandas as pd
from shapely.geometry import Polygon, Point
import folium
import itertools

df = gaming_companies.top_3_cities_location()


import pandas as pd
from shapely.geometry import Polygon, Point
import folium
import itertools

def create_city_map(df, city_name):
    """
    Generates a map for a specified city with markers for the two farthest points within a threshold distance,
    the midpoint between these points, and a polygon covering all the points within the threshold.
    Args:
    - df: DataFrame containing the data.
    - city_name: Name of the city to generate the map for.
    Returns:
    - Folium map object.
    """

    # Filter DataFrame for entries corresponding to the specified city
    city_df = df[df['City'] == city_name]

    # Check if there is data for the specified city
    if city_df.empty:
        print(f"No data available for {city_name}.")
        return None

    # Initialize map centered on the average coordinates of the city
    initial_centroid = Point(city_df['Longitude'].mean(), city_df['Latitude'].mean())
    map = folium.Map(location=[initial_centroid.y, initial_centroid.x], zoom_start=12)

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

    # Compute midpoint of the two farthest points to represent the city center
    midpoint_lat = (point1[0] + point2[0]) / 2
    midpoint_lon = (point1[1] + point2[1]) / 2

    # Calculate radius from midpoint to farthest point, convert to meters for map visualization
    radius_in_meters = (max_distance / 4) * 111320  # Rough conversion from degrees to meters

    # Add markers for the farthest points and midpoint to the map
    folium.Marker([point1[0], point1[1]], popup='Point 1').add_to(map)
    folium.Marker([point2[0], point2[1]], popup='Point 2').add_to(map)
    folium.Marker([midpoint_lat, midpoint_lon], popup='Midpoint').add_to(map)

    # Draw a circle around the midpoint to represent the coverage radius
    folium.Circle([midpoint_lat, midpoint_lon], radius=radius_in_meters, color='red', fill=True, fill_opacity=0.2).add_to(map)

    # Construct a polygon from the filtered city coordinates and add it to the map
    polygon_points = list(zip(filtered_df['Latitude'], filtered_df['Longitude']))
    folium.Polygon(locations=polygon_points, color='blue', fill=True, fill_color='blue').add_to(map)
    return map



def city_map_san_francisco_companies():
    """
    Generates and returns a Folium map for the city of San Francisco.
    The map includes markers for the two farthest points within a threshold distance, 
    the midpoint between these points, and a polygon covering nearly all the points within the threshold.
    """
    city_map_san_francisco = create_city_map(df, 'San Francisco')
    return city_map_san_francisco

def city_map_new_york_companies():
    """
    Generates and returns a Folium map for the city of New York.
    The map includes markers for the two farthest points within a threshold distance, 
    the midpoint between these points, and a polygon covering nearly all the points within the threshold.
    """
    city_map_new_york = create_city_map(df, 'New York')
    return city_map_new_york

def city_map_london_companies():
    """
    Generates and returns a Folium map for the city of London.
    The map includes markers for the two farthest points within a threshold distance, 
    the midpoint between these points, and a polygon covering nearly all the points within the threshold.
    """
    city_map_london = create_city_map(df, 'London')
    return city_map_london


