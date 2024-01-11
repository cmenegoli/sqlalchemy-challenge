# sqlalchemy-challenge

"""
This project uses Python and SQLAlchemy to perform basic data exploration and analysis of an SQLite climate database.
All analysis is done using SQLAlchemy ORM queries, Pandas, and Matplotlib.
It also provides an API, designed using Flask, for querying the climate data.
"""

## Part I: Exploratory Climate Analysis

"""
This part of the project analyzes Hawaii precipitation and weather station data, and produces visualizations of rainfall and temperature patterns.
It also supports the planning of visits to Hawaii by providing local precipitation summaries for each weather station and daily temperature data for a flexible range of trip dates.
"""

# Components of Part I:
"""
- SQLite database: Resources/Hawaii.sqlite
- Jupyter notebook: sqlalchemy-challenge/climate_analysis.ipynb (uses SQLAlchemy, Python Pandas, and Matplotlib)
- Visualizations: Bar charts, histogram, and area chart (visible within the notebook and stored as .png files in the sqlalchemy-challenge folder)
"""

## Part II: Climate App

"""
This part of the project exposes several SQLAlchemy precipitation and temperature queries through an API using a Python Flask app.
The available endpoints are:
"""

# Endpoints of Part II:
"""
- Home page: /
- Precipitation: /api/v1.0/precipitation (returns daily precipitation totals for the last year)
- Stations: /api/v1.0/stations (returns active weather stations)
- Temperature Observations: /api/v1.0/tobs (returns daily temperature observations for the WAIHEE weather station)
- Trip: /api/v1.0/trip/yyyy-mm-dd (returns minimum, average, and maximum temperatures for the range beginning with the provided start date through 08/23/17)
- Trip Range: /api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd (returns minimum, average, and maximum temperatures for the range beginning with the provided start and end date)
"""

# Components of Part II:
"""
- SQLite database: Resources/Hawaii.sqlite
- Flask app: sqlalchemy-challenge/app.py
"""


