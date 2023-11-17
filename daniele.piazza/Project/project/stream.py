import streamlit as st
from location import Location
from visualize import City,Country
import pandas as pd
import os
#Change .streamlit/config.toml to change the theme color, the map will change accordingly

_="""
 This file contains the streamlit app.
It contains the following methods:
    - load_location: load the location data
    - load_city_data: load the city data
    - load_country_data: load the country data
    - create_html: create the html files for the heatmaps
    - load_html: load the html files for the heatmaps
    - choose_dataset: choose the dataset to display
    - display_statistics: display the statistics of the dataset
    - display_heatmap: display the heatmap of the dataset
    - display_boxplot: display the boxplot of the dataset
    - display_line_chart: display the line chart of the dataset
    - display_prediction: display the prediction of the dataset
    - display_line_year: display the line chart of the dataset for a specific year
"""

update = False # Set to True if you want to update the coordinates of the cities in the csv files
st.set_page_config(layout="wide")
api_key = pd.read_csv("/Users/dani/Desktop/api_key.txt",header=None)[0][0] #change with your google api key
all_path = "Data/GlobalLandTemperaturesByCity.csv"
major_path = "Data/GlobalLandTemperaturesByMajorCity.csv"
country_path = "Data/GlobalLandTemperaturesByCountry.csv"

_="""
Load the location data

Parameters
----------
path : str
    Path of the CSV file
api_key : str
    Google API key

Returns
-------
location : Location
    Location object
"""
@st.cache_data
def load_location(path, api_key):
    location = Location(path, api_key)
    if update:
        location.update_file()
    return location

_="""
Load the city data

Parameters
----------
data : pandas.core.frame.DataFrame
    Dataframe with the city, country, latitude and longitude

Returns
-------
city : City
    City object
"""
@st.cache_data
def load_city_data(data):
    city = City(data)
    return city

_="""
Load the country data

Parameters
----------
path : str
    Path of the CSV file

Returns
-------
country : Country
    Country object
"""
@st.cache_data
def load_country_data(path):
    country = Country(path)
    return country

location_major = load_location(major_path, api_key)
location_all = load_location(all_path, api_key)
major = load_city_data(location_major.data)
all = load_city_data(location_all.data)
country = load_country_data(country_path)

_="""
Create the html files for the heatmaps
"""
def create_html():
    major.temperature().write_html("temperature_major.html")
    major.range().write_html("range_major.html")
    all.temperature().write_html("temperature_all.html")
    all.range().write_html("range_all.html")

_="""
Load the html files for the heatmaps. If the file doesn't exist, create it.

Parameters
----------
path : str
    Path of the html file

Returns
-------
html : str
    Html file
"""
@st.cache_data
def load_html(path):
    if not os.path.exists(path):
        create_html()
    with open(path, 'r') as f:
        return f.read()
    
_="""
Choose the dataset to display

Returns
-------
location : Location
    Location object
vis : City
    City object
temperature : str 
    Html file for the temperature heatmap
range : str
    Html file for the range heatmap
"""
def choose_dataset():
    dataset = st.radio("Choose a dataset", ("Major cities", "All cities"))
    if dataset == "Major cities":
        location = location_major
        st.write("This dataset includes climate data from major cities around the world.")
        vis = major
        temperature = load_html("temperature_major.html")
        range = load_html("range_major.html")
    else:
        location = location_all
        st.write("This dataset includes climate data from all cities around the world.")
        vis = all
        temperature = load_html("temperature_all.html")
        range = load_html("range_all.html")
    return location, vis, temperature, range

_="""
Display the statistics of the dataset

Parameters
----------
data : City or Country
    City or Country object
label : str
    Label of the dataset
"""
def display_statistics(data,label):
    st.subheader("Dataset Statistics")
    stats = data.additional_statistics()
    stats = stats.rename(columns={
        'AverageTemperature': 'Average Temperature',
        'MinTemperature': 'Minimum Temperature',
        'MaxTemperature': 'Maximum Temperature',
        'Std': 'Standard Deviation',
    })
    stats.index.name = label if isinstance(data, City) else "Country"
    st.dataframe(stats, width=1400, height=420)

_="""
Display the heatmap of the dataset

Parameters
----------
data : City or Country
    City or Country object
title : str
    Title of the heatmap
label : str
    Label of the dataset
number : int
    Number of cities to display
max : int
    Maximum number of cities
html : str
    Html file for the heatmap
"""
def display_heatmap(data, title, label, number = None, max = None, html = None):
    st.subheader(title)
    average = True if title.endswith("Average Temperature Heatmap") else False
    caption = "average" if average else "range (max-min)"
    st.caption("This heatmap displays the {} of the temperatures for each {} in the dataset.".format(caption, label))
    if number == max and html is not None:
        st.components.v1.html(html, width=1400, height=800, scrolling=True)
    else:
        st.plotly_chart(data.range(number) if average else data.temperature(number))

_="""
Display the boxplot of the dataset

Parameters
----------
data : City or Country
    City or Country object
selected : str
    Selected city or country
"""
def display_boxplot(data, selected):
    st.subheader("Temperature Boxplot for {}".format(selected))
    st.caption("This boxplot shows the distribution of temperatures for {} overviewing each month.".format(selected))
    boxplot = data.boxplot(selected)
    st.plotly_chart(boxplot)

_="""
Display the line chart of the dataset

Parameters
----------
data : City or Country
    City or Country object
selected : str
    Selected city or country
"""
def display_line_chart(data, selected):
    st.subheader("Temperature Line Chart for {}".format(selected))
    st.caption("This line chart shows the temperature trends for {} over the years.".format(selected))
    fig = data.line(selected)
    st.plotly_chart(fig)

_="""
Display the prediction of the dataset

Parameters
----------
data : City or Country
    City or Country object
selected : str
    Selected city or country
"""
def display_prediction(data, selected):
    st.subheader("Temperature's Prediction")
    st.caption("This line chart shows the predicted temperatures for the next 50 years.")
    predicted_temperatures = data.predict_temperature(selected)
    st.plotly_chart(predicted_temperatures)

_="""
Display the line chart of the dataset for a specific year

Parameters
----------
data : City or Country
    City or Country object
selected : str
    Selected city or country
year : int
    Selected year
"""
def display_line_year(data, selected, year):
    st.subheader(f"Climate Data for {selected} in {year}")
    st.caption(f"This line chart shows the temperatures for {selected} during the months of {year}.")
    fig = data.line_year(selected,year)
    st.plotly_chart(fig)

def main():
    st.title("Global Climate Data Analysis")
    page = st.selectbox("Select a page", ("General Cities Data", "Specific City Information","General Countries Data","Specific Country Information"))
    if page == "General Cities Data":
        location, vis, temperature, range = choose_dataset()
        display_statistics(vis,"City")
        max = vis.data_year['City_Country'].nunique()
        st.subheader("Temperature Range Heatmap")
        number_range = st.number_input("Choose the number of cities with the most significant temperature range to display on the map. Enter a number from 1 to {}.".format(max), min_value=1, max_value=max, value=max)
        display_heatmap(vis, "Temperature Range Heatmap", "city", number_range, max, range)
        st.subheader("Average Temperature Heatmap")
        number_temp = st.number_input("Choose the number of hottest cities to display on the temperature map. Enter a number from 1 to {}.".format(max), min_value=1, max_value=max, value=max)
        display_heatmap(vis, "Average Temperature Heatmap", "city", number_temp, max, temperature)
    elif page == "Specific City Information":
        location, vis, temperature, range = choose_dataset()
        unique_country = location.data['Country'].unique()
        unique_country.sort()
        selected_country = st.selectbox("Choose a Country", ("All", *unique_country))
        if selected_country != "All":
            city_list = location.data[location.data['Country'] == selected_country]['City_Country'].unique()
        else:
            city_list = location.data['City_Country'].unique()
        city_list.sort()
        selected_city = st.selectbox("Choose a City", city_list,placeholder="Select a city",index=None)
        if selected_city is not None:
            st.subheader(f"Climate Data for {selected_city}")
            st.plotly_chart(vis.show_city(selected_city))
            display_boxplot(vis, selected_city)
            display_line_chart(vis, selected_city)
            display_prediction(vis, selected_city)
            selected_year = st.selectbox("Choose a year", vis.data_year[vis.data_year['City_Country']==selected_city]['Year'].unique())
            display_line_year(vis, selected_city, selected_year)
    elif page == "General Countries Data":
        display_statistics(country,"Country")
        display_heatmap(country, "Temperature Range Heatmap", "country")
        display_heatmap(country, "Average Temperature Heatmap", "country")
    elif page == "Specific Country Information":
        continent = country.data['Continent'].unique()
        continent.sort()
        selected_continent = st.selectbox("Choose a Continent", ("All", *continent))
        if selected_continent != "All":
            country_list = country.data[country.data['Continent'] == selected_continent]['Country'].unique()
        else:
            country_list = country.data['Country'].unique()
        country_list.sort()
        selected_country = st.selectbox("Choose a Country", country_list,placeholder="Select a country",index=None)
        if selected_country is not None:
            st.subheader(f"Climate Data for {selected_country}")
            display_boxplot(country, selected_country)
            display_line_chart(country, selected_country)
            display_prediction(country, selected_country)
            selected_year = st.selectbox("Choose a year", country.data_year[country.data_year['Country']==selected_country]['Year'].unique())
            display_line_year(country, selected_country, selected_year)


if __name__ == "__main__":
    main()