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

comment on table public.fuel_prices is 'Records of fuel prices.';

comment on column public.fuel_prices.station_id is 'Same as "id" in "stations" table. Because query is based on geo_hash, which may not be unique to stations, "station_id" in this table may not be in the stations table.';

comment on column public.fuel_prices.fuel_type is 'The fuel type symbol. D - Diesel; numbers - Research Octane Number (RON).';

comment on column public.fuel_prices.brand is 'Brand of the fuel station. If missing, the station''s brand is unknown in "gaspy".';

comment on column public.fuel_prices.latitude is 'Latitude of the location of the fuel station.';

comment on column public.fuel_prices.longitude is 'Longitude of the location of the fuel station.';

comment on column public.fuel_prices.price is 'Price of the fuel corresponding to "fuel_type" and uploaded at "updated_time", in unit of NZD per 100L.';

comment on column public.fuel_prices.update_time is 'The time that the fuel price is uploaded. It cannot be earlier than 1 days before the data is fetched.';

alter table public.fuel_prices
    owner to neondb_owner;

