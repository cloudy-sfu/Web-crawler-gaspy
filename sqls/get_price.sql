SELECT fuel_type, price, update_time
FROM fuel_prices
WHERE station_id = :station_id
ORDER BY update_time