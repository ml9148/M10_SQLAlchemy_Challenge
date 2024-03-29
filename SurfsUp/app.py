# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement_info = Base.classes.measurement
station_info = Base.classes.station

# Create our session (link) from Python to the DB

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return '''
        <h2>Available routes:</h2>
        <ul>
            <li>/api/v1.0/precipitation</li>
            <li>/api/v1.0/station</li>
            <li>/api/v1.0/tobs</li>
            <li>/api/v1.0/[start]</li>
            <li>/api/v1.0/[start]/[end]</li>
        </ul>
        '''

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    return [ {d:p} for d,p in session.query(measurement_info.date, measurement_info.prcp).filter(measurement_info.date>='2016-08-23').all()]

@app.route('/api/v1.0/station')
def stations():
    session = Session(engine)

    results=session.query(Station.station, Station.name).all()
    session.close()
    #return [ {id:loc} for id,loc in results]
    stations= list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
     session = Session(engine)

     queryresult = session.query( measurement_info.date, measurement_info.tobs).filter(measurement_info.station=='USC00519281')\
     .filter(measurement_info.date>='2016-08-23').all()
     session.close()
     tob_obs = []
     for date, tobs in queryresult:
         tobs_dict = {}
         tobs_dict["Date"] = date
         tobs_dict["Tobs"] = tobs
         tob_obs.append(tobs_dict)
 
     return jsonify(tob_obs)

@app.route("/api/v1.0/<start>")

def get_temps_start(start):
    session = Session(engine)
    results = session.query(func.min(measurement_info.tobs), func.avg(measurement_info.tobs), func.max(measurement_info.tobs)).\
              filter(measurement_info.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dictionary = {}
        temps_dictionary['Minimum Temperature'] = min_temp
        temps_dictionary['Average Temperature'] = avg_temp
        temps_dictionary['Maximum Temperature'] = max_temp
        temps.append(temps_dictionary)

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(measurement_info.tobs), func.avg(measurement_info.tobs), func.max(measurement_info.tobs)).\
              filter(measurement_info.date >= start).filter(measurement_info.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dictionary = {}
        temps_dictionary['Minimum Temperature'] = min_temp
        temps_dictionary['Average Temperature'] = avg_temp
        temps_dictionary['Maximum Temperature'] = max_temp
        temps.append(temps_dictionary)

    return jsonify(temps)
                   
if __name__ == '__main__':
    app.run()