SELECT DISTINCT ON (fp.station_id)
    fp.station_id, fp.price, fp.brand, s.name, s.latitude, s.longitude
FROM public.fuel_prices fp
    JOIN public.stations s
ON fp.station_id = s.station_id
WHERE fp.fuel_type = :fuel_type
ORDER BY fp.station_id, fp.update_time DESC