import os
import requests
import json
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
from . import companies_gaming

# Connect DB Database
token = os.getenv("token")
# Connect to MongoDB client
client = MongoClient("localhost:27017")
client.list_database_names()
db = client["Project_III"]
# Access the specified database and collection
starbucks = db.get_collection("Starbucks")

# Geocoding: Converting a place name / address into geographic coordinates

def url_geocode(where):
    url_geocode = f"https://geocode.xyz/{where}?json=1"
    response = requests.get(url_geocode)
    return response.json()

#In case you want to save the Starbucks data in MongoDB you will have to create a Databse called: Project_III and a Collection called: Starbucks
def upload_collection(c_name, list_):
    db = client.get_database("Project_III")
    c = db[c_name]
    for item in list_:
        c.insert_one(item)
# Save downloaded infromation into a JSON and work locally
def save_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Retrieve the midpoint coordinates for San Francisco
sf_lat, sf_lon, sf_radius = companies_gaming.midpoint_coordinates_radius_sf()
# Retrieve the midpoint coordinates for New York
ny_lat,nylon, ny_radius  = companies_gaming.midpoint_coordinates_radius_ny()
# Retrieve the midpoint coordinates for London
ldn_lat, ldn_lon, ld_radius = companies_gaming.midpoint_coordinates_radius_ldn()

#Create a connection to Foursquare API in order to find out about what we have around a given radius

def request_4sq(query, lat, lon, radius = 3700, sort_by = "DISTANCE", limit = 50):
    url = f"https://api.foursquare.com/v3/places/search?query={query}&ll={lat}%2C{lon}&radius={radius}&sort={sort_by}&limit={limit}"
    headers = {"accept": "application/json", "Authorization": token}
    try:
        return requests.get(url, headers = headers).json()
    except:
        print("Request not found")

def foursq_top3_cities_query(query,c_name):
    request_sf = request_4sq(query, sf_lat, sf_lon, radius=int(sf_radius/ 4))
    request_ny = request_4sq(query, ny_lat, nylon, radius=int(ny_radius/ 4))
    request_ld = request_4sq(query, ldn_lat, ldn_lon, radius=int(ld_radius/ 4))
    #In case you want to save the query data in MongoDB you will have to create a Databse called: Project_III and a Collection called: quer_name

    list_of_query_sf = request_sf['results']  
    upload_collection(c_name, list_=list_of_query_sf)
    list_of_query_ny = request_ny['results']  
    upload_collection(c_name, list_=list_of_query_ny)
    list_of_query_ld = request_ld['results']  
    upload_collection(c_name, list_=list_of_query_ld) 
    
    """
    Counts the occurrences of documents in a specified MongoDB collection for each given city.
    Args:
    - collection_name: Name of the MongoDB collection.
    - cities: List of cities to count occurrences in.
    Returns:
    - DataFrame with counts for each city.
    """
    
    client = MongoClient("localhost:27017")
    db = client["Project_III"]
    collection = db.get_collection(c_name)
    cities = ['San Francisco', 'New York', 'London']

    # Dictionary to store the counts for each city
    city_counts = {city: 0 for city in cities}

    # Query the collection and count the locations for each city
    for city in cities:
        count = collection.count_documents({"location.locality": city})
        city_counts[city] = count

    # Convert the dictionary to a DataFrame
    return pd.DataFrame(list(city_counts.items()), columns=['City', f'{c_name} Count'])

def weighted_count_merged_df():
    """
    Aggregates and normalizes the counts of various categories (Starbucks, Schools, Clubs, and Bars)
    across three major cities. This function queries data for each category, merges them into a single DataFrame,
    and then normalizes these counts on a scale of 0 to 1. An average percentage score is then calculated 
    for each city based on these normalized values.

    The function relies on the foursq_top3_cities_query function to fetch the count of each category in the cities.
    The normalization helps in comparing the prevalence of each category relative to the city with the highest count.

    Returns:
    - A DataFrame sorted by the average percentage (weighted score) of the normalized counts for each category.
    """
    df_Starbucks_count = foursq_top3_cities_query(query="Starbucks",c_name="Starbucks")
    df_School_count = foursq_top3_cities_query(query="School",c_name="Schools")
    df_Club_count = foursq_top3_cities_query(query="Club",c_name="Club")
    df_Bar_count = foursq_top3_cities_query(query="Bar",c_name="Bar")
    
    #API has a limit of 50, so the redundancy of this infromation is low. As there could be a clear inner here. One thing is sure, London has less in the radius given
    df_merged = df_School_count.merge(df_Starbucks_count, on='City')
    df_merged = df_merged.merge(df_Club_count, on='City')
    df_merged = df_merged.merge(df_Bar_count, on='City')

    df_merged['Schools Count Normalized'] = df_merged['Schools Count'] / df_merged['Schools Count'].max()
    df_merged['Starbucks Count Normalized'] = df_merged['Starbucks Count'] / df_merged['Starbucks Count'].max()
    df_merged['Clubs Count Normalized'] = df_merged['Club Count'] / df_merged['Club Count'].max()
    df_merged['Bars Count Normalized'] = df_merged['Bar Count'] / df_merged['Bar Count'].max()

    # Apply weights
    weights = {
        'Schools': 0.20,
        'Starbucks': 0.20,
        'Clubs': 0.20,
        'Bars': 0.40
    }
    # Calculate average percentage
    df_merged['Weighted Score'] = (df_merged['Schools Count Normalized'] + 
                                   df_merged['Starbucks Count Normalized'] + 
                                   df_merged['Clubs Count Normalized'] + 
                                   df_merged['Bars Count Normalized']) / 4

    # Sort by the weighted score
    return df_merged.sort_values(by='Weighted Score', ascending=False)

