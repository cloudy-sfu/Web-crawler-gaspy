"""
Roam in the fuel map and capture response from the server. When circled number still
exist in the current window, zoom in until there are only single stations.
The map uses quadtree to store locations. (e.g. Google's S2 or Uber’s H3)
"""
import json
import os
from natsort import natsorted
import pandas as pd

base_dir = 'stations'
stations = []
stations_in_queries = []
for fn_city in os.listdir(base_dir):
    fp_city = os.path.join(base_dir, fn_city)
    if os.path.isdir(fp_city):
        fn_queries = natsorted(os.listdir(fp_city))
        for fn_query in fn_queries:
            fp_query = os.path.join(fp_city, fn_query)
            with open(fp_query) as f:
                response = json.load(f)
            data = response.get('data')
            if not isinstance(data, list):
                continue
            n = 0
            for station in data:
                if int(station.get('totalPrices', 0)) != 1:
                    continue
                n += 1
                station_ = {
                    "id": station.get('stationKey'),
                    "city": fn_city,
                    "name": station.get('stationName'),
                    "geo_hash": station.get('geoHash'),
                }
                stations.append(station_)
            stations_in_queries.append(n)
stations = pd.DataFrame(stations)
stations.drop_duplicates(subset=['id'], inplace=True)
stations.set_index(['id'], inplace=True)
stations.to_csv(os.path.join(base_dir, "stations.csv"))
with open(os.path.join(base_dir, "max_stations"), "w") as f:
    # The batch size should not exceed this value.
    f.write(str(max(stations_in_queries)))
