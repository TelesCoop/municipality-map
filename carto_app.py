import json

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium, folium_static

st.title('Visualisation des mairies')

@st.cache_data
def load_data():
    df = pd.read_excel("export_CVU.xlsx")
    # https://stackoverflow.com/questions/35491274/split-a-pandas-column-of-lists-into-multiple-columns
    # https://stackoverflow.com/questions/38231591/split-explode-a-column-of-dictionaries-into-separate-columns-with-pandas
    df2 = df['centre'].map(eval).apply(pd.Series)
    # df2 = pd.json_normalize(df['centre'])

    df3 = pd.DataFrame(df2["coordinates"].to_list(), columns=['longitude', 'latitude'])
    df[['longitude', 'latitude']] = df3[['longitude', 'latitude']]
    #df = pd.concat([df.drop(['centre'], axis=1), df['centre'].apply(pd.Series)], axis=1)

    #st.dataframe(df)
    #st.table(df)
    return df


def times_to_str(times):
    return ", ".join([f"{time['de'][:5]}-{time['a'][:5]}" for time in times])


df = load_data()


with st.sidebar:
    text_input = st.text_input('Recherche', '')
    population_min_input = st.slider('Population min', 0, 300000, 10000)
    population_max_input = st.slider('Population max', 0, 300000, 50000)

m = folium.Map(location=[df.latitude.quantile(.5), df.longitude.quantile(.5)], 
                 zoom_start=5, control_scale=True)

columns=['nom', 'Code du département',
       'Libellé du département', 'codesPostaux',
       'population', 'horaires', 'email',
       'telephone', 'url', 'Nom de l\'élu',
       'Prénom de l\'élu', 'Date de naissance',
       'Libellé de la catégorie socio-professionnelle',
       'Date de début du mandat', 'Date de début de la fonction']


df_filtered = df.copy()
if text_input:
    df_filtered = df[df['nom'].str.contains(text_input, case=False) | df['Libellé du département'].str.contains(text_input, case=False)]

df_filtered = df_filtered[(df_filtered['population'] >= population_min_input) & (df_filtered['population'] <= population_max_input)]

#Loop through each row in the dataframe
for i,row in df_filtered.iterrows():

    popup_content = ""
    #Setup the content of the popup
    for column in columns:
        if column not in row.index:
            continue
        if column == 'codesPostaux':
            postal_codes = json.loads(row[column].replace("'", '"'))

            popup_content += f"<div><b>{column.title()}</b>: {', '.join(postal_codes)}</div>"
        elif column == 'horaires':
            if type(row[column]) is float:
                continue
            hours = json.loads(row[column].replace("'", '"'))
            hours_str = "".join([f"<li>Du {hour['du']} au {hour['au']} : {times_to_str(hour['heures'])}</li>" for hour in hours])
            popup_content += f"<div><b>{column.title()}</b>: <ul>{hours_str}</ul></div>"
        else:
            popup_content += f"<div><b>{column.title()}</b>: {row[column]}</div>"

    #Initialise the popup using the iframe
    popup = folium.Popup(f"<div>{popup_content}</div>", min_width=300, max_width=300)
    # popup = folium.Popup(f"<div>{popup_content}</div>", min_width=700, max_width=1000)

    #Add each row to the map
    folium.Marker(location=[row['latitude'],row['longitude']],
                  popup = popup, c=row['nom']).add_to(m)
#https://towardsdatascience.com/3-easy-ways-to-include-interactive-maps-in-a-streamlit-app-b49f6a22a636
#st_data = st_folium(m, width=700)
st_data = folium_static(m, width=1000)

