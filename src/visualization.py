from . import companies_gaming
from . import foursquare
from shapely.geometry import Point
import folium
import itertools
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas as pd

client = MongoClient("localhost:27017")
db = client["Project_III"]

df_companies_gaming = companies_gaming.top_3_cities_location()
foursquare.foursq_top3_cities_query

def create_city_map(df_companies_gaming, city_name):
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
    city_df = df_companies_gaming[df_companies_gaming['City'] == city_name]

    # Check if there is data for the specified city
    if city_df.empty:
        print(f"No data available for {city_name}.")
        return None

    # Initialize map centered on the average coordinates of the city
    initial_centroid = Point(city_df['Longitude'].mean(), city_df['Latitude'].mean())
    map = folium.Map(location=[initial_centroid.y, initial_centroid.x], zoom_start=12)

    # Add markers for each company
    for _, row in city_df.iterrows():
        icon = folium.Icon(
            color="darkblue",
            icon_color="white",
            icon="fa-building",
            prefix="fa",
        )
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"{row['Company Name']}<br>{row['Street']}",
            icon=icon
        ).add_to(map)

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

    return map



def city_map_san_francisco_companies():
    """
    Generates and returns a Folium map for the city of San Francisco.
    The map includes markers for the two farthest points within a threshold distance, 
    the midpoint between these points, and a polygon covering nearly all the points within the threshold.
    """
    city_map_san_francisco = create_city_map(df_companies_gaming, 'San Francisco')
    return city_map_san_francisco

def city_map_new_york_companies():
    """
    Generates and returns a Folium map for the city of New York.
    The map includes markers for the two farthest points within a threshold distance, 
    the midpoint between these points, and a polygon covering nearly all the points within the threshold.
    """
    city_map_new_york = create_city_map(df_companies_gaming, 'New York')
    return city_map_new_york

def city_map_london_companies():
    """
    Generates and returns a Folium map for the city of London.
    The map includes markers for the two farthest points within a threshold distance, 
    the midpoint between these points, and a polygon covering nearly all the points within the threshold.
    """
    city_map_london = create_city_map(df_companies_gaming, 'London')
    return city_map_london


def create_dual_pie_charts(category1, category2, category3, category4):
    """
    Creates two separate figures, each with two pie charts, to visualize the distribution 
    of four different data categories. This function also includes a third figure showing 
    the distribution of the average weighted score. This visualization helps in comparing 
    different categories across multiple cities.
    
    Args:
    - category1: First data category for the first figure.
    - category2: Second data category for the first figure.
    - category3: First data category for the second figure.
    - category4: Second data category for the second figure.
    
    The function fetches data using foursquare.weighted_count_merged_df(), then creates 
    pie charts with both count and percentage for each category and city.
    """
    df_companies_gaming = foursquare.weighted_count_merged_df()

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
    axes1[0].pie(df_companies_gaming[category1 + ' Count'], labels=df_companies_gaming['City'], autopct=make_autopct(df_companies_gaming[category1 + ' Count']), startangle=140)
    axes1[0].set_title(f'Distribution of {category1}')

    axes1[1].pie(df_companies_gaming[category2 + ' Count'], labels=df_companies_gaming['City'], autopct=make_autopct(df_companies_gaming[category2 + ' Count']), startangle=140)
    axes1[1].set_title(f'Distribution of {category2}')

    # Second figure
    axes2[0].pie(df_companies_gaming[category3 + ' Count'], labels=df_companies_gaming['City'], autopct=make_autopct(df_companies_gaming[category3 + ' Count']), startangle=140)
    axes2[0].set_title(f'Distribution of {category3}')

    axes2[1].pie(df_companies_gaming[category4 + ' Count'], labels=df_companies_gaming['City'], autopct=make_autopct(df_companies_gaming[category4 + ' Count']), startangle=140)
    axes2[1].set_title(f'Distribution of {category4}')

    # Third figure

    axes3.pie(df_companies_gaming['Weighted Score'], labels=df_companies_gaming['City'], autopct=make_autopct(df_companies_gaming['Weighted Score']), startangle=140)
    axes3.set_title('Distribution of Weighted Score')

    # Show the figures
    return plt

def build_map():
    """
    Builds and returns a Folium map for New York City, with additional markers for 
    various categories such as Starbucks, Bars, Clubs, and Schools. Each category 
    is represented with a unique icon and color.

    The function fetches data from MongoDB collections for each category, combines 
    them into a single DataFrame, and then plots each location on the map with a 
    customized icon. This map provides a visual representation of different 
    points of interest within the city.
    """

    map = city_map_new_york_companies()
    def create_df_from_collection(collection):
        data = []
        for doc in collection.find():
            # Extracting latitude and longitude
            lat = doc.get('geocodes', {}).get('main', {}).get('latitude')
            lon = doc.get('geocodes', {}).get('main', {}).get('longitude')

            # Extracting name
            chains = doc.get('chains', [])
            if chains:
                name = chains[0].get('name')  # Use name from 'chains' if available
            else:
                name = doc.get('name')  # Otherwise, use the 'name' field

            # Extracting address and locality
            address = doc.get('location', {}).get('formatted_address')
            locality = doc.get('location', {}).get('locality')

            # Append data if all information is present
            if lat and lon and name and address and locality:
                data.append({'Name': name, 'Address': address, 'Locality': locality, 'Latitude': lat, 'Longitude': lon})

        return pd.DataFrame(data)

    def combined_df():
        # Create DataFrames for each category
        df_starbucks = create_df_from_collection(db.get_collection("Starbucks"))
        df_bar = create_df_from_collection(db.get_collection("Bar"))
        df_club = create_df_from_collection(db.get_collection("Club"))
        df_schools = create_df_from_collection(db.get_collection("Schools"))

        # Combine all DataFrames
        return pd.concat([df_starbucks, df_bar, df_club, df_schools], ignore_index=True)

    df = combined_df()

    groups = {
        'Starbucks': folium.FeatureGroup(name='Starbucks'),
        'Bar': folium.FeatureGroup(name='Bar'),
        'Club': folium.FeatureGroup(name='Club'),
        'School': folium.FeatureGroup(name='School')
    }

    for _, row in df.iterrows():
        # Determine the icon and group based on the category
        if 'Starbucks' in row['Name']:
            icon_color, icon, group = "green", "coffee", groups['Starbucks']
        elif 'Bar' in row['Name']:
            icon_color, icon, group = "blue", "fa-id-card", groups['Bar']
        elif 'Club' in row['Name']:
            icon_color, icon, group = "black", "music", groups['Club']
        elif 'School' in row['Name']:
            icon_color, icon, group = "red", "fa-graduation-cap", groups['School']
        else:
            continue  # Skip if the category is not recognized

        # Create a folium Icon
        folium_icon = folium.Icon(color=icon_color, icon=icon, prefix='fa')

        # Create a Marker within the appropriate group
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"{row['Name']}<br>{row['Address']}",
            icon=folium_icon
        ).add_to(group)

    # Add each FeatureGroup to the map
    for group in groups.values():
        group.add_to(map)

    # Add LayerControl to toggle groups
    folium.LayerControl().add_to(map)

    return map

