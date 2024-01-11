# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
Measurement = Base.classes.measurement
Station = Base.classes.station

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

@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = str(latest_date)
    latest_date_df = dt.datetime.strptime(latest_date, "%Y-%m-%d").date()
    
     # Calculate the date one year from the last date in data set
    year_ago = latest_date_df - dt.timedelta(days=365)
    
     # Perform a query to retrieve the data and precipitation scores
    data_scores = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= year_ago).all()
    )
    data_df = pd.DataFrame(data_scores)
    data_df = data_df.rename(columns={"date": "Date", "prcp": "Precipitation (in)"})
    

    # Sort the dataframe by date
    sorted_df = data_df.sort_values(by=["Date"], ascending=True)
    data_dict = sorted_df.to_dict("split")["data"]
    
    return jsonify(data_dict)
    
@app.route("/api/v1.0/stations")
def stations():
    data = session.query(Station.station).all()
    session.close()
    results = list(np.ravel(data))
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = "USC00519281"
    most_recent_date = session.query(func.max(Measurement.date)).first()
    most_recent_date = str(most_recent_date)
    most_recent_as_dt = datetime.strptime(most_recent_date, "('%Y-%m-%d',)").date()
    one_year_ago = most_recent_as_dt - dt.timedelta(days=365)

    temp_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    temp_dict = [{"date": date, "temp": temp} for date, temp in temp_data]

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>", defaults={"end": None})
@app.route("/api/v1.0/<start>/<end>")
def determine_temps_for_date_range(start, end):
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # If we have both a start date and an end date.
    if end != None:
        temperature_data = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs),
            )
            .filter(Measurement.date >= start)
            .filter(Measurement.date <= end)
            .all()
        )
    # If we only have a start date.
    else:
        temperature_data = (
            session.query(
                Measurement.date,
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs),
            )
            .filter(Measurement.date >= start)
            .all()
        )

    session.close()

    # Convert the query results to a list.
    temperature_list = []
    no_temperature_data = False
    for min_temp, avg_temp, max_temp in temperature_data:
        if min_temp == None or avg_temp == None or max_temp == None:
            no_temperature_data = True
        temperature_list.append(min_temp)
        temperature_list.append(avg_temp)
        temperature_list.append(max_temp)
    # Return the JSON representation of dictionary.
    if no_temperature_data == True:
        return f"No temperature data found for the given date range. Try another date range."
    else:
        return jsonify(temperature_list)

    
if __name__=="__main__":
    app.run(debug=True)