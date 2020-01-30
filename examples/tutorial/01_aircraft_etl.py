from aircraftlib import (
    Position,
    surrounding_area,
    fetch_aircraft_vectors,
    Database,
    clean_vector,
    add_airline_info,
    fetch_airlines,
    fetch_routes,
    fetch_equipment,
    fetch_airports,
)

# pull data, store to DB
# pull data periodically (hourly), append to DB
# sqlalchemy for ORM to sqlite local DB (build engine, session, and query objects)
# store raw vectors? or normallize in another way?
# pandas read to dataframe: df = pd.read_sql(query.statement, query.session.bind)

# ETL:
#   - progress to parameters:
#       - Fetch within an area (position, radius, disable)
#       - Enable/Disable update reference data

# analysis:
#   - how many AC from each airline are in the sky right now?
#   - Frequency management via clustering
#   - Plot current flights (just dots)
#   - Plot current routes (great circle distance)
#   - Correlate current flights with known routes
#   - Plot pariclar AC path over time (requires historical data)


def main():
    # Fetch starting location based on airport (parameterize)
    # TODO: fetch position from reference data
    dulles_airport_position = Position(lat=38.9519444444, long=-77.4480555556)

    # Get the live AC vector data around this airport
    radius_km = 200
    area_surrounding_dulles = surrounding_area(dulles_airport_position, radius_km)
    # area_surrounding_dulles = None

    # Fetch the data
    print("fetching reference data...")
    airlines_ref_data = fetch_airlines()
    airports_ref_data = fetch_airports()
    route_ref_data = fetch_routes()
    equipment_ref_data = fetch_equipment()

    print("fetching live aircraft vectors...")
    raw_ac_vectors = fetch_aircraft_vectors(
        area=area_surrounding_dulles
    )  # , offline=True)

    print("cleaning & transform vectors...")
    transformed_vectors = []
    for raw_vector in raw_ac_vectors["states"]:
        vector = clean_vector(raw_vector)
        if vector:
            add_airline_info(vector, airlines_ref_data)
            transformed_vectors.append(vector)

    print("saving vectors...")
    db = Database()
    db.add_aircraft_vectors(transformed_vectors)

    print("saving reference data...")
    db.update_airlines(airlines_ref_data)
    db.update_airports(airports_ref_data)
    db.update_routes(route_ref_data)
    db.update_equipment(equipment_ref_data)


if __name__ == "__main__":
    main()
