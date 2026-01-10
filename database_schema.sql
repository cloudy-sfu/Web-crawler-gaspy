--
-- PostgreSQL database dump
--

\restrict 3V2b3KK8AkGBtGQd3VfcSicGt7LOIz1stZaNNhhven16WoMxgZlmUhY2L1YuEJm

-- Dumped from database version 17.7 (e429a59)
-- Dumped by pg_dump version 17.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_table_access_method = heap;

--
-- Name: fuel_prices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fuel_prices (
    station_id character varying(32),
    fuel_type character varying(8),
    brand character varying(32),
    price numeric(6,1),
    update_time timestamp with time zone
);


--
-- Name: TABLE fuel_prices; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.fuel_prices IS 'Records of fuel prices.';


--
-- Name: COLUMN fuel_prices.station_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.fuel_prices.station_id IS 'Same as "id" in "stations" table. Because query is based on geo_hash, which may not be unique to stations, "station_id" in this table may not be in the stations table.';


--
-- Name: COLUMN fuel_prices.fuel_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.fuel_prices.fuel_type IS 'The fuel type symbol. D - Diesel; numbers - Research Octane Number (RON).';


--
-- Name: COLUMN fuel_prices.brand; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.fuel_prices.brand IS 'Brand of the fuel station. If missing, the station''s brand is unknown in "gaspy".';


--
-- Name: COLUMN fuel_prices.price; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.fuel_prices.price IS 'Price of the fuel corresponding to "fuel_type" and uploaded at "updated_time", in unit of NZD per 100L.';


--
-- Name: COLUMN fuel_prices.update_time; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.fuel_prices.update_time IS 'The time that the fuel price is uploaded. It cannot be earlier than 1 days before the data is fetched.';


--
-- Name: stations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stations (
    station_id character(32) NOT NULL,
    name text,
    geo_hash character varying(8),
    latitude double precision,
    longitude double precision
);


--
-- Name: TABLE stations; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.stations IS 'Information of fuel stations.';


--
-- Name: COLUMN stations.station_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.stations.station_id IS '`Original "station_key" in "gaspy", the identifier of the fuel station.';


--
-- Name: COLUMN stations.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.stations.name IS 'Name of the fuel station.';


--
-- Name: COLUMN stations.geo_hash; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.stations.geo_hash IS 'Geometry hash code of quadtree, which is used by "gaspy" to search fuel stations.';


--
-- Name: fuel_prices fuel_prices_uniq_1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_prices
    ADD CONSTRAINT fuel_prices_uniq_1 UNIQUE (station_id, fuel_type, update_time);


--
-- Name: stations stations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_pkey PRIMARY KEY (station_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 3V2b3KK8AkGBtGQd3VfcSicGt7LOIz1stZaNNhhven16WoMxgZlmUhY2L1YuEJm

