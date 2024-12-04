from itertools import count

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import streamlit as st
import pydeck as pdk


default_types = ["large_airport", "medium_airport", "small_airport"]

#read in data

def read_data():
    return pd.read_csv('new_england_airports.csv').set_index("id")

print(read_data())

# filter

def filter_data(sel_states, sel_types):
    df = read_data()
    if sel_states:
        df = df.loc[df['iso_region'].isin(sel_states)]
    if sel_types:
        df = df.loc[df['type'].isin(sel_types)]
    return df

def all_states():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['iso_region'] not in lst:
            lst.append(row['iso_region'])

    return lst



# count frequency of state
def count_states(states, df):

    lst = [df.loc[df['iso_region'].isin([state])].shape[0] for state in states]
    return lst

def state_types(df):

    type = [row['type'] for ind, row in df.iterrows()]
    states = [row['iso_region'] for ind, row in df.iterrows()]

    dict = {}

    for state in states:
        dict[state] = []

    for i in range(len(type)):
        dict[states[i]].append(type[i])

    return dict


def state_sums(dict_types):
    dict = {}
    for key in dict_types.keys():
        dict[key] = len(dict_types[key])
    return dict






# pie chart
def generate_pie_chart(counts, sel_states):
    plt.figure()
    explodes = [0 for i in range(len(counts))]
    maximum = counts.index(np.max(counts))
    explodes[maximum] = .25
    plt.pie(counts, labels=sel_states, explode = explodes, autopct = "%.2f")
    plt.title(f"Distribution of Selected Size Airports by State: {', '.join(sel_states)}")

    return plt

##bar chart
def generate_bar_chart(dict_sums):
    x = dict_sums.keys()
    y = dict_sums.values()

    plt.figure()
    plt.bar(x, y)
    plt.xticks(rotation = 45)
    plt.ylabel("State")
    plt.xlabel(f"Number of Airports")
    plt.title(f"Number of Selected Size Airports by State: {', '.join(dict_sums.keys())}")


    return plt
##map
def generate_map(df):
    map_df = df.filter(['name', 'latitude_deg', 'longitude_deg'])

    view_state = pdk.ViewState(latitude=map_df['latitude_deg'].mean(),
                               longitude=map_df['longitude_deg'].mean(),
                               zoom = 6)
    layer  = pdk.Layer("ScatterplotLayer",
                       data = map_df,
                       get_position='[longitude_deg, latitude_deg]',
                       get_radius = 50,
                       get_color = [20, 175, 250])
    tool_tip = {"html": "<b>Airport:<br/><b>{name}</b>",
                "style": {"backgroundColor": "steelblue",
                          "color": "white"}}
    text_layer = pdk.Layer(
        "TextLayer",
        data=df,
        get_position="[longitude_deg, latitude_deg-.01]",
        get_text="name",
        get_size=7,
        get_color=[0, 0, 0])

    ###chat gpt assist
    icon_data = {
        "url": "https://png.pngtree.com/png-vector/20220502/ourmid/pngtree-airplane-silhouette-fly-png-image_4561790.png",
        "width": 200,
        "height": 200,
        "anchorY": 128}
    df['icon_data'] = [icon_data] * len(df)

    icon_layer = pdk.Layer(
        "IconLayer",
        data=df,
        get_icon="icon_data",
        get_position="[longitude_deg, latitude_deg]",
        get_size=18,
        pickable = True)
    ### end of chat gpt help

    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers = [layer, icon_layer],
                   tooltip= tool_tip)
    st.pydeck_chart(map)

## bacground color (chat gpt)
def set_background_color(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color} ! important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def main():
    color = st.sidebar.color_picker("Pick a background color", value="#FFC3A0")#, "#848463", "#fb968a", "#a0c5c4", "#86664b"])
    set_background_color(color)

    st.title("Airport Visualization")
    st.write("Learn more about the airports of New England")

    ##sidebar filters
    st.sidebar.write("Choose your options to show data:")
    states = st.sidebar.multiselect("Select states: ", all_states())
    type = st.select_slider("Select airport size:",
                            options = ['small_airport','medium_airport','large_airport',],
                            value = 'small_airport'  )

    data = filter_data(states, [type])
    series = count_states(states, data)

    ##check for filters
    if len(states) > 0 and type is not None:
        st.write("View a map of airports")
        generate_map(data)

        st.write("View a pie chart of chosen size airports in selected states")
        st.pyplot(generate_pie_chart(series, states))

        st.write("View a bar chart of count of chosen size airports in selected states")
        types = state_types(data)
        sums = state_sums(types)

        st.pyplot(generate_bar_chart(sums))




main()
