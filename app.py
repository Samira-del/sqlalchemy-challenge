import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Flask Setup
app = Flask(__name__)

@app.route("/")
def index():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"####################################<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/><br/>"
        f"############## NOTE #################<br/>"
        f"(Enter start and end date like YYYY-MM-DD)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Return the precipitation data for the last year
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    prcp_date = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    precip = {date: prcp for date, prcp in prcp_date}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    # Return a list of stations
    results = session.query(Station.station).all()

    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Return the temperature observations (tobs) for previous year
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()
    tobs_list = list(np.ravel(results))
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # Return TMIN, TAVG, TMAX
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        tobs_list = list(np.ravel(results))
        return jsonify(tobs_list)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)


if __name__ == '__main__':
    app.run()
