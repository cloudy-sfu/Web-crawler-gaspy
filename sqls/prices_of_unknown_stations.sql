select *
from fuel_prices
where station_id not in (select distinct station_id from stations)
order by station_id, update_time