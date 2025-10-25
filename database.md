# Database

This document includes the description of database.

[TOC]



## Meta data

| Attribute           | Value        |
| ------------------- | ------------ |
| SQL dialect         | `postgresql` |
| SQL dialect version | 17           |
| Cloud service       | Neon         |
| Schema              | `public`     |



## Tables

### `stations`

DDL:

```
create table public.stations
(
    id       char(32),
    city     varchar(16),
    name     text,
    geo_hash varchar(8)
);
```

Description:

| Name       | Description                                                  |
| ---------- | ------------------------------------------------------------ |
| `id`       | Originally `station_key` in `gaspy`, the identifier of the fuel station. |
| `city`     | The location of the fuel station. All stations are approximately (not strictly follow political administrative divisions) classified into 4 cities: Auckland, Wellington, Hamilton, Christchurch. |
| `name`     | Name of the fuel station.                                    |
| `geo_hash` | Geometry hash code of quadtree, which is used by `gaspy` to search fuel stations. |



### `fuel_prices`

DDL:

```
create table public.fuel_prices
(
    station_id  varchar(32),
    fuel_type   varchar(8),
    brand       varchar(32),
    latitude    double precision,
    longitude   double precision,
    price       numeric(6, 1),
    update_time timestamp with time zone,
    constraint fuel_prices_uniq_1
        unique (station_id, fuel_type, update_time)
);
```

Description:

| Name          | Description                                                  |
| ------------- | ------------------------------------------------------------ |
| `station_id`  | Originally `station_key` in `gaspy`, the identifier of the fuel station. **Because query is based on `geo_hash`, which may not be unique to stations, `station_id` in this table may not be in the stations table.** |
| `fuel_type`   | The fuel type symbol. See the fuel types table.              |
| `brand`       | Brand of the fuel station. If missing, the station's brand is unknown in `gaspy`. |
| `latitude`    | Latitude of the location of the fuel station.                |
| `longitude`   | Longitude of the location of the fuel station.               |
| `price`       | Price of the fuel corresponding to `fuel_type` and uploaded at `updated_time`, in unit of NZD per 100L. |
| `update_time` | The time that the fuel price is uploaded. It cannot be earlier than 1 days before the data is fetched. |

