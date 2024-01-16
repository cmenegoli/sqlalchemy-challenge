# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc, func

from flask import Flask,jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
     #Listing avaiable API roots
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/>start<<br/>"
        f"/api/v1.0/>start>/>end<<br/>"
        f"For >start< and >end< enter your desired start and end date"
        "<br/>"
    )
    #ROUTE SOURCE - precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Open session
    session = Session(engine)
    
    latest_date = session.query(func.max(measurement.date)).scalar()
    latest_date = str(latest_date)
    latest_date_df = dt.datetime.strptime(latest_date, "%Y-%m-%d").date()
    
     # Calculate the date one year from the last date in data set
    year_ago = latest_date_df - dt.timedelta(days=365)
    
     # Perform a query to retrieve the data and precipitation scores
    data_scores = (
        session.query(measurement.date, measurement.prcp)
        .filter(measurement.date >= year_ago).all()
    )
     #Close session
    session.close()
    
    data_df = pd.DataFrame(data_scores)
    data_df = data_df.rename(columns={"date": "Date", "prcp": "Precipitation (in)"})
    

    # Sort the dataframe by date
    sorted_df = data_df.sort_values(by=["Date"], ascending=True)
    data_dict = sorted_df.to_dict("split")["data"]
    
    return jsonify(data_dict)

    #ROUTE SOURCE - stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    data = session.query(station.station).all()
    session.close()
    results = list(np.ravel(data))
    
    session.close()
    
    return jsonify(results)

    #ROUTE SOURCE - tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_active_stations = (session
                            .query(measurement.station, func.count(measurement.station).label('count'))
                            .group_by(measurement.station)
                            .order_by(desc('count'))
                            .all())
    station_last_date = (session.query(func.max(measurement.date))
                         .filter(measurement.station == most_active_stations[0][0])
                         .scalar())
    
    #Convert station_last_date to a datetime object
    station_last_date = dt.datetime.strptime(station_last_date, '%Y-%m-%d').date()

    #Calculate one year prior
    year_prior = station_last_date - dt.timedelta(days=365)
    
    #Perform left join for the measurment and station tables
    query_2= (session.query(measurement, station.name)
               .outerjoin(station, measurement.station == station.station)
               .filter(measurement.station == most_active_stations[0][0])
               .filter(measurement.date >= str(year_prior))
               .all())

    session.close()
    
    #Loop over the query_2 results to fatch the results needed to create the jsonified result
    result_list = []
    for row in query_2:
        measurement_data = {
            'date': row[0].date,
            'tobs': row[0].tobs,
            'station': row[0].station,
            'station_name': row[1]  
        }
        result_list.append(measurement_data)

    return jsonify(result_list)

@app.route('/api/v1.0/<start_date>')
def start_date(start_date):
    try:
        #Convert the input date string to a datetime object
        start = dt.datetime.strptime(start_date, '%Y-%m-%d').date()

        session = Session(engine)

        #Query the results from start date onwards based on a user start date
        results = (session.query(
            func.min(measurement.tobs).label('min'),
            func.avg(measurement.tobs).label('avg'),
            func.max(measurement.tobs).label('max')
        ).filter(measurement.date >= start)
        .group_by(measurement.date)
        .all())

        session.close()

        result_dict = []

        for row in results:
            dictionary = {
                'min': row.min,
                'avg': row.avg,
                'max': row.max
            }
            result_dict.append(dictionary)

        return jsonify(result_dict)

    except ValueError:
        #If the date format is incorrect, return an error message
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400
    

#ROUTE SOURCE - <start_date>/<end>
@app.route('/api/v1.0/<start_date>/<end>')
def start_end(start_date, end):
    try:
        #Convert the input date string to a datetime object
        start = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()

        session = Session(engine)

        #Query the results based on two parameters: the start and end periods that a user provides. 
        results = (session.query(
            func.min(measurement.tobs).label('min'),
            func.avg(measurement.tobs).label('avg'),
            func.max(measurement.tobs).label('max')
        ).filter(measurement.date >= start, measurement.date <= end_date)
        .group_by(measurement.date)
        .all())

        session.close()

        #Creating a dictionary to hold the results before we jsonify them
        result_dict = []
        for row in results:
            dictionary = {
                'min': row.min,
                'avg': row.avg,
                'max': row.max
            }
            result_dict.append(dictionary)

        return jsonify(result_dict)

    except ValueError:
        # If the date format is incorrect, return an error message
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400

if __name__=="__main__":
    app.run(debug=True)