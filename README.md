# Web crawler "gaspy"

 Record petrol and diesel fuel prices in major New Zealand cities

![](https://shields.io/badge/dependencies-Python_3.12-blue)

## Acknowledgement

Data source: [gaspy](https://www.gaspy.nz/)



## Usage

This program records petrol and diesel fuel prices, that drivers physically read from oil pumps in fuel stations and uploaded to "gaspy" website, in major New Zealand cities. See file `stations/stations.csv` for the list of fuel stations. The meaning of the columns are as follows.

| Name       | Data type | Description                                                  |
| ---------- | --------- | ------------------------------------------------------------ |
| `id`       | `str`     | Originally `station_key` in `gaspy`, the identifier of the fuel station. |
| `city`     | `str`     | The location of the fuel station. All stations are approximately (not strictly follow political administrative divisions) classified into 4 cities: Auckland, Wellington, Hamilton, Christchurch. |
| `name`     | `str`     | Name of the fuel station.                                    |
| `geo_hash` | `str`     | Geometry hash code of quadtree, which is used by `gaspy` to search fuel stations. |

Go to "data" branch and download the data of any date. For example, folder `2025-04` means the data of 2025 April. File `2025-04-20` means the current fuel prices at approximately (script triggered time may have about 10 minutes delay) 2025-04-20 6:00 UTC.

The meaning of columns are as follows.

| Name           | Data type                                                    | Description                                                  |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `station_id`   | `str`                                                        | Originally `station_key` in `gaspy`, the identifier of the fuel station. **Because query is based on `geo_hash`, which may not be unique to stations, `station_id` in this table may not be in the stations table.** |
| `fuel_type`    | `str`                                                        | The fuel type symbol. See the fuel types table.              |
| `brand`        | `str`                                                        | Brand of the fuel station. If missing, the station's brand is unknown in `gaspy`. |
| `latitude`     | `float`                                                      | Latitude of the location of the fuel station.                |
| `longitude`    | `float`                                                      | Longitude of the location of the fuel station.               |
| `price`        | `float`                                                      | Price of the fuel corresponding to `fuel_type` and uploaded at `updated_time`, in unit of NZD per 100L. |
| `updated_time` | [`pandas.Timestamp`](https://pandas.pydata.org/docs/reference/api/pandas.Timestamp.html) | The time that the fuel price is uploaded. It cannot be earlier than 1 days before the data is fetched. |

The meaning of fuel types are as follows.

| Symbol | Meaning            |
| ------ | ------------------ |
| 91     | Petrol unleaded 91 |
| 95     | Petrol unleaded 95 |
| 98     | Petrol unleaded 98 |
| D      | Diesel fuel        |

GitHub Actions record updated prices of the past day in 6:00 UTC every day.

- 18:00 New Zealand standard time
- 19:00 New Zealand daylight saving time

The data will be updated to "data" branch.
