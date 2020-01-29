from sqlalchemy import Column, DateTime, String, Integer, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

# OpenSky API states/all reference
# Source: https://opensky-network.org/apidoc/rest.html#all-state-vectors
# 0  icao24             string      Unique ICAO 24-bit address of the transponder in hex string representation.
# 1  callsign           string      Callsign of the vehicle (8 chars). Can be null if no callsign has been received.
# 2  origin_country     string      Country name inferred from the ICAO 24-bit address.
# 3  time_position      int         Unix timestamp (seconds) for the last position update. Can be null if no position report was received by OpenSky within the past 15s.
# 4  last_contact       int         Unix timestamp (seconds) for the last update in general. This field is updated for any new, valid message received from the transponder.
# 5  longitude          float       WGS-84 longitude in decimal degrees. Can be null.
# 6  latitude           float       WGS-84 latitude in decimal degrees. Can be null.
# 7  baro_altitude      float       Barometric altitude in meters. Can be null.
# 8  on_ground          boolean     Boolean value which indicates if the position was retrieved from a surface position report.
# 9  velocity           float       Velocity over ground in m/s. Can be null.
# 10 true_track         float       True track in decimal degrees clockwise from north (north=0°). Can be null.
# 11 vertical_rate      float       Vertical rate in m/s. A positive value indicates that the airplane is climbing, a negative value indicates that it descends. Can be null.
# 12 sensors            int[]       IDs of the receivers which contributed to this state vector. Is null if no filtering for sensor was used in the request.
# 13 geo_altitude       float       Geometric altitude in meters. Can be null.
# 14 squawk             string      The transponder code aka Squawk. Can be null.
# 15 spi                boolean     Whether flight status indicates special purpose indicator.
# 16 position_source    int         Origin of this state’s position: 0 = ADS-B, 1 = ASTERIX, 2 = MLAT


class AircraftVector(Base):
    # PK: a physical AC at a specific time
    __tablename__ = "aircraft_vector"

    icao = Column(String, primary_key=True)
    callsign = Column(String, nullable=True)
    origin_country = Column(String)
    time_position = Column(Integer, nullable=True)
    last_contact = Column(Integer, primary_key=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    baro_altitude = Column(String, nullable=True)
    on_ground = Column(Boolean)
    velocity = Column(Float)
    true_track = Column(Float, nullable=True)
    vertical_rate = Column(Float, nullable=True)
    geo_altitude = Column(Float, nullable=True)
    squawk = Column(String, nullable=True)
    spi = Column(Boolean)
    position_source = Column(Integer)


class Database:
    def __init__(self):
        self.engine = create_engine("sqlite:///aircraft-db.sqlite")
        session_maker = sessionmaker()
        session_maker.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.session = session_maker()

    def add_aircraft_vectors(self, vectors):
        for entry in vectors:
            new_entry = entry[:]
            new_entry.pop(12)
            vec = AircraftVector(
                **dict(zip(AircraftVector.__table__.columns.keys(), new_entry))
            )
            # insert or update vector
            self.session.merge(vec)

        # cannot bulk insert or update vectors
        # self.session.bulk_save_objects(objects)
        self.session.commit()
