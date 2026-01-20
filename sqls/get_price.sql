SELECT fuel_type, price, update_time
FROM fuel_prices
WHERE station_id = :station_id
    and update_time > now() - INTERVAL '6 months'
ORDER BY update_time