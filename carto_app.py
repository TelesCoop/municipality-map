import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium, folium_static

st.title('Visualisation des mairies')

df = pd.read_excel("export_CVU.xlsx").head(100)
# https://stackoverflow.com/questions/35491274/split-a-pandas-column-of-lists-into-multiple-columns
# https://stackoverflow.com/questions/38231591/split-explode-a-column-of-dictionaries-into-separate-columns-with-pandas
df2 = df['centre'].map(eval).apply(pd.Series)
#df2 = pd.json_normalize(df['centre'])

df3 = pd.DataFrame(df2["coordinates"].to_list(), columns=['longitude', 'latitude'])
df[['longitude', 'latitude']] = df3[['longitude', 'latitude']]

#df = pd.concat([df.drop(['centre'], axis=1), df['centre'].apply(pd.Series)], axis=1)


#st.dataframe(df)
#st.table(df)

m = folium.Map(location=[df.latitude.quantile(.5), df.longitude.quantile(.5)], 
                 zoom_start=5, control_scale=True)

columns=['nom', 'Code du département',
       'Libellé du département', 'codesPostaux',
       'population', 'horaires', 'email',
       'telephone', 'url', 'Nom de l\'élu',
       'Prénom de l\'élu', 'Date de naissance',
       'Libellé de la catégorie socio-professionnelle',
       'Date de début du mandat', 'Date de début de la fonction']

#Loop through each row in the dataframe
for i,row in df.iterrows():
    
    #Setup the content of the popup
    iframe = folium.IFrame(str(pd.DataFrame(row[columns]).to_html(header=False))) # row["Well Name"]
    
    #Initialise the popup using the iframe
    popup = folium.Popup(iframe, min_width=700, max_width=1000)
    
    #Add each row to the map
    folium.Marker(location=[row['latitude'],row['longitude']],
                  popup = popup, c=row['nom']).add_to(m)
#https://towardsdatascience.com/3-easy-ways-to-include-interactive-maps-in-a-streamlit-app-b49f6a22a636
#st_data = st_folium(m, width=700)
st_data = folium_static(m, width=1000)

