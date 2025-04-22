import json
import logging
import random
import time
import uuid
from argparse import ArgumentParser

import pandas as pd
from requests import Session
from tqdm import tqdm
import sys

# %% Initialize.
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
)
parser = ArgumentParser()
parser.add_argument('--github_action', action='store_true')
parser.add_argument('--email', type=str, required=True,
                    help='gaspy.nz account email')
parser.add_argument('--password', type=str, required=True,
                    help='gaspy.nz account password')
cmd, _ = parser.parse_known_args()
with open("header/dart_header.json") as f:
    dart_header = json.load(f)
with open("stations/max_stations") as f:
    chunk_size = int(f.read())

# %% Pre-process stations.
stations = pd.read_csv("stations/stations.csv")
stations.sort_values(by='geo_hash', inplace=True)
stations['geo_hash_len'] = stations['geo_hash'].apply(len)
stations_chunks = []
for length, subset in stations.groupby('geo_hash_len'):
    for i in range(0, subset.shape[0], chunk_size):
        stations_chunks.append(subset.iloc[i:i+chunk_size])

# %% Login.
session = Session()
response = session.post(
    url="https://gaspy.nz/api/v1/Public/login",
    data=json.dumps({
        "email": cmd.email,
        "password": cmd.password,
        "gold_key": None,
        "v": 22,
        "a": "3.21.3",
    }),
    headers=dart_header,
)
if response.status_code != 200:
    raise Exception(f"Status code: {response.status_code}. Reason: {response.reason}")
assert response.json().get('success'), "gaspy.nz username and password don't match."
response_json = response.json()
fuel_types = response_json['data']['fuel_types']
fuel_types = {
    meta['code']: int(key)  # unsafe conversion, aim to raise problems before query.
    for key, meta in fuel_types.items()
}
brands = response_json['data']['brands']
selected_fuel_types = ['91', 'D', '95', '98']
assert all(fuel_type in fuel_types.keys() for fuel_type in selected_fuel_types), \
    "Some of petrol #91, #95, #98 or diesel don't have a fuel type ID."

# %% Query map data.
now = pd.Timestamp('now', tz='UTC')
start_time = now - pd.Timedelta(days=1)
device_id = str(uuid.uuid4()).upper()
pbar = tqdm(desc="Record fuel prices",
            total=len(selected_fuel_types) * len(stations_chunks))
prices = []


def safe_astype(ins, cls):
    try:
        return cls(ins)
    except (ValueError, TypeError):
        return pd.NA


for fuel_type in selected_fuel_types:
    fuel_type_id = fuel_types[fuel_type]
    price_per_type = []
    for chunk in stations_chunks:
        geo_hash_list = chunk['geo_hash'].tolist()
        response = session.post(
            url="https://gaspy.nz/api/v1/Map/blocksFromHashcodes",
            data=json.dumps({
                "hashcodes": geo_hash_list,
                "fuel_type_id": fuel_type_id,
                "fuel_type_code": fuel_type,
                "gold_key": None,
                "ev_plug_types": [],
                "v": "22",
                "a": "3.21.3",
                "udid": "ios_" + device_id,
            })
        )
        time.sleep(random.uniform(0.7, 1.3))
        if response.status_code != 200:
            logging.warning(f"Geometry hash region fails: {geo_hash_list} "
                            f"Status code: {response.status_code}. Reason: {response.reason}")
            continue
        response_json = response.json()
        if not response_json.get('success'):
            logging.warning(f"Geometry hash region fails: {geo_hash_list} "
                            f"gaspy.nz returns errors: {response_json.get('error')}")
            continue
        data = response_json.get('data')
        if not isinstance(data, list):
            logging.warning(f"Fail to parse the response of geometry hash region "
                            f"{geo_hash_list}")
        for station in data:
            updated_time_str = station.get('dateUpdated', '')
            updated_time_naive = pd.to_datetime(
                updated_time_str, format="%Y-%m-%dT%H:%M:%S.%fZ", errors='coerce')
            updated_time = updated_time_naive.tz_localize(tz='UTC', nonexistent='NaT')
            if updated_time >= start_time:
                price = {
                    "station_id": station.get('stationKey', pd.NA),
                    "brand": brands.get(station.get('brandId'), pd.NA),
                    "latitude": safe_astype(station.get('lat'), float),
                    "longitude": safe_astype(station.get('lng'), float),
                    "fuel_type": fuel_type,
                    "price": safe_astype(station.get('price'), float),
                    f"updated_time": updated_time,
                }
                prices.append(price)
        pbar.update(1)
prices = pd.DataFrame(prices)
prices.drop_duplicates(subset=['station_id', 'fuel_type'], inplace=True)
prices.set_index(['station_id', 'fuel_type'], inplace=True)
if cmd.github_action:
    prices.to_csv(f"/tmp/{now.strftime("%Y-%m-%d")}.csv")
else:
    prices.to_csv(f"{now.strftime("%Y-%m-%d")}.csv")
