import json
import os

from natsort import natsorted

base_dir = 'stations'
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
            stations_in_queries.append(n)
with open(os.path.join(base_dir, "max_stations"), "w") as f:
    f.write(str(max(stations_in_queries)))
# The batch size should not exceed this value.
