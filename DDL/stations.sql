create table public.stations
(
    id       char(32),
    city     varchar(16),
    name     text,
    geo_hash varchar(8)
);

comment on table public.stations is 'Information of fuel stations.';

comment on column public.stations.id is '`Original "station_key" in "gaspy", the identifier of the fuel station.';

comment on column public.stations.city is 'The location of the fuel station. All stations are approximately (not strictly follow political administrative divisions) classified into 4 cities: Auckland, Wellington, Hamilton, Christchurch.';

comment on column public.stations.name is 'Name of the fuel station.';

comment on column public.stations.geo_hash is 'Geometry hash code of quadtree, which is used by "gaspy" to search fuel stations.';

alter table public.stations
    owner to neondb_owner;

