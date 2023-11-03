import os
from dotenv import load_dotenv
load_dotenv() # load_env
from pymongo import MongoClient
import pandas as pd
from collections import defaultdict

cc = os.getenv("credit_card")
token = os.getenv("token")



def find_top_10_gaming_cities():
    client = MongoClient("localhost:27017")
    client.list_database_names()
    db = client["Ironhack"]
    c = db.get_collection("companies")
    filter_1 = {
        "tag_list": {"$regex": "gaming", "$options": "i"}
    }

    projection = {"_id": 0, "offices.city": 1}

    query = list(c.find(filter_1, projection).sort("name", -1))

    city_counts = defaultdict(int)

    for item in query:
        for office in item['offices']:
            city = office.get('city', '')
            if city:  # Check if city is not empty or None
                city_counts[city] += 1

    # Sort by value in descending order
    sorted_city_counts = {k: v for k, v in sorted(city_counts.items(), key=lambda item: item[1], reverse=True)}
    
    # Take top 10 cities
    top_10_cities = dict(list(sorted_city_counts.items())[:10])

    return pd.DataFrame(list(top_10_cities.items()), columns=['City', 'Count'])