import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station=Base.classes.station
measurement = Base.classes.measurement

app = Flask(__name__)

@app.route("/")
def welcome():
    return(
        f"Available Routes:<br/>"
        f"Precipitaion: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"dates and temperature observations of the most active station for the last year of data: /api/v1.0/tobs<br/>"
        f"Temperature from start date(format:yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature from start to end date(format:yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"

    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    results=session.query(*[measurement.date,measurement.prcp]).all()
    session.close()

    precipitation=[]
    for date, prcp in results:
        precipitation_df={}
        precipitation_df['date']=date
        precipitation_df['prcp']=prcp
        precipitation.append(precipitation_df)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results=session.query(Station.station, Station.name).all()

    session.close()

    stations=[]
    for station, name in results:
        station_df={}
        station_df['station']=station
        station_df['name']=name

        stations.append(station_df)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    lastest_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
    lastest_date=dt.datetime.strptime(lastest_date, '%Y-%m-%d')
    one_year_earlier=dt.date(lastest_date.year-1,lastest_date.month,lastest_date.day)
    results=session.query(measurement.date, measurement.tob).filter(measurement.date>=one_year_earlier).all()
    session.close()

    tobs=[]

    for date, tobs in results:
        tobs_df={}
        tobs_df['date']=date
        tobs_df['tobs']=tobs
        tobs.append(tobs_df)
    
    return jsonify(tobs)
@app.route("/api/v1.0/<start>")
def start_date(start):
    session=Session(engine)
    result=session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date>=start).all()
    session.close()

    tob_start=[]
    for min,max,avg in result:
        tob_start_df={}
        tob_start_df['min']=min
        tob_start_df['max']=max
        tob_start_df['avg']=avg
        tob_start.append(tob_start_df)

    return jsonify(tob_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session=Session(engine)
    result=session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date>=start).filter(measurement.date<=end).all()
    session.close()

    tob_start_end=[]
    for min,max,avg in result:
        tob_start_end_df={}
        tob_start_end_df['min']=min
        tob_start_end_df['max']=max
        tob_start_end_df['avg']=avg
        tob_start_end.append(tob_start_end_df)
        
    return jsonify(tob_start_end)

if __name__ == '__main__':
    app.run(debug=True)