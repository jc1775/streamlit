import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime
import plotly.express as px

DATA_URL=(
    "conposcovidloc.csv"
)

st.title("Covid-19 Cases Reported in Ontario")
st.markdown("### This application uses official data to visualize and analyze covid-19 cases in Ontario")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL,nrows=nrows)
    data.dropna(subset=['Reporting_PHU_Latitude','Reporting_PHU_Longitude'], inplace=True)
    lowercase= lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'reporting_phu_longitude':'longitude','reporting_phu_latitude': 'latitude','reporting_phu_city': 'city','reporting_phu': 'reporting_organization', 'outcome1':'outcome'}, inplace=True)
    data.drop(labels="client_gender",axis='columns', inplace=True)
    data.drop(labels="outbreak_related",axis='columns', inplace=True)
    data.drop(labels="reporting_phu_address",axis='columns', inplace=True)
    data.drop(labels="reporting_phu_postal_code",axis='columns', inplace=True)
    data.drop(labels="reporting_phu_website",axis='columns', inplace=True)
    data.drop(labels="case_acquisitioninfo",axis='columns', inplace=True)
    data.drop(labels="row_id",axis='columns', inplace=True)
    data= data[data.age_group != 'Unknown']
    return data

data = load_data(100000)
age_range=np.array(data['age_group'])
age_range_unique=np.unique(age_range)
age_range_unique_list=age_range_unique.tolist()
age_range_unique_list.insert(0,'all')

st.header("Where are the Covid-19 cases located in Ontario?")
age_group = st.selectbox(
    "Age Group",
    age_range_unique_list
)

start_date=data.accurate_episode_date.min()
start_year=int(start_date[:4])
start_month=int(start_date[5:7])
start_day=int(start_date[8:])

end_date=data.accurate_episode_date.max()
end_year=int(end_date[:4])
end_month=int(end_date[5:7])
end_day=int(end_date[8:])

start_date = st.date_input('start date',datetime.date(start_year,start_month,start_day))
end_date = st.date_input('end date',datetime.date(end_year,end_month,end_day))

if end_date > start_date:
    data=data[data.accurate_episode_date <= str(end_date)]
    data=data[data.accurate_episode_date >= str(start_date)]
else:
    st.markdown("# Start date must be prior to end date")

if age_group == 'all':
    #st.map(data[["latitude","longitude"]].dropna(how="any"))
    data = data
else:
    #st.map(data.query("age_group == @age_group")[["latitude","longitude"]].dropna(how="any"))
    data = data[data.age_group == age_group]

num_cities = np.array(data.city)
unique, counts = np.unique(num_cities, return_counts=True)
city_count = dict(zip(unique,counts))
max_cases = int(max(city_count.values()))
midpoint = (np.average(data['latitude']),np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 5,
        "pitch": 50
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['latitude','longitude']],
        get_position=['longitude','latitude'],
        radius=10000,
        extruded=True,
        pickable=True,
        elevation_scale=max_cases,
        elevation_range=[0,25],
        ),
    ],
))


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)



chart_data = pd.DataFrame.from_dict(city_count,orient='index')
#print(chart_data)

fig=px.bar(chart_data,height=400)
st.write(fig)
