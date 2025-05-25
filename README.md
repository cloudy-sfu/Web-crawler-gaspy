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

It publishes a dataset at [hugging face](https://huggingface.co/datasets/cloudy-sfu/Gaspy/tree/main).

GitHub Actions record updated prices of the past day in 6:00 UTC every day.

- 18:00 New Zealand standard time
- 19:00 New Zealand daylight saving time

