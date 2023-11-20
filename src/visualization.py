from . import companies_gaming
from . import foursquare
from shapely.geometry import Polygon, Point

import pandas as pd

import folium
import itertools

import matplotlib.pyplot as plt

df = companies_gaming.top_3_cities_location()


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


def create_dual_pie_charts(category1, category2, category3, category4):
    """
    Creates two separate figures, each with three pie charts, for comparing four different data categories
    and the average weighted score.
    Args:
    - category1: First data category for the first figure.
    - category2: Second data category for the first figure.
    - category3: First data category for the second figure.
    - category4: Second data category for the second figure.
    """
    df = foursquare.weighted_count_merged_df()

    # Function for autopct to show count and percentage
    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            count = int(round(pct*total/100.0))
            return f'{count} ({pct:.1f}%)'
        return my_autopct

    # Create two figures, each with three subplots
    fig1, axes1 = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))
    fig2, axes2 = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))
    fig3, axes3 = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))


    # First figure
    axes1[0].pie(df[category1 + ' Count'], labels=df['City'], autopct=make_autopct(df[category1 + ' Count']), startangle=140)
    axes1[0].set_title(f'Distribution of {category1}')

    axes1[1].pie(df[category2 + ' Count'], labels=df['City'], autopct=make_autopct(df[category2 + ' Count']), startangle=140)
    axes1[1].set_title(f'Distribution of {category2}')

    # Second figure
    axes2[0].pie(df[category3 + ' Count'], labels=df['City'], autopct=make_autopct(df[category3 + ' Count']), startangle=140)
    axes2[0].set_title(f'Distribution of {category3}')

    axes2[1].pie(df[category4 + ' Count'], labels=df['City'], autopct=make_autopct(df[category4 + ' Count']), startangle=140)
    axes2[1].set_title(f'Distribution of {category4}')

    # Third figure

    axes3.pie(df['Weighted Score'], labels=df['City'], autopct=make_autopct(df['Weighted Score']), startangle=140)
    axes3.set_title('Distribution of Weighted Score')

    # Show the figures
    return plt.show()