#Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Set up database engine
engine = create_engine("sqlite:///hawaii.sqlite")

#Reflect database into our classes
Base = automap_base()
Base.prepare(engine, reflect=True)

#Create a variable for each of the classes
Measurement = Base.classes.measurement
Station = Base.classes.station 

#Create a session link from Python to our database
session = Session(engine)

#Define our Flask app
app = Flask(__name__)

#Define the welcome route
@app.route('/')
def welcome():  #create a welcome function
    return(
    ''' 
    Welcome to the Climate Analysis API!<br/>
    Available Routes:<br/>
    /api/v1.0/precipitation<br/>
    /api/v1.0/stations<br/>
    /api/v1.0/tobs<br/>
    /api/v1.0/temp/start/end
    ''')
@app.route("/api/v1.0/precipitation") ##define a precipitation route
def precipitation():                  #cerate a  precipitation function
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365) 
    precipitation = session.query(Measurement.date, Measurement.prpc).\
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation} #create accomodation for JSON file   
    return jsonify(precip)
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))    
    return jsonify(temps=temps) 
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >=start).all()
        temps = list(np.ravel(results))    
        return jsonify(temps=temps)

    results = session.query(*sel).\
        filter(Measurement.date >=start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)               