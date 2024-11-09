#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
from connection import main

#######################
# Page configuration
st.set_page_config(
    page_title="IlluminateMe Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Color illuminateMe #599191
# Color in eye #51be9e
# Color orange #ffd966
# Color blue in eye #2a2f64

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
#main()
df_energy = pd.read_csv('energy-irl-results.csv')

#######################
# Selection functions

### ENERGY
def energy_differ(df_energy_date):
    data_e = {
        'energy': df_energy_date['calorie'].values,
        'time':df_energy_date['time'].values,
        'label': ['in_out'] * len(df_energy_date)
        }
    df_e = pd.DataFrame(data_e)
    data_acc = {
        'energy': df_energy_date['calorie_acc'].values,
        'time':df_energy_date['time'].values,
        'label': ['calorie_acc'] * len(df_energy_date)
        }
    df_acc = pd.DataFrame(data_acc)
    df_energy_date_final = pd.concat([df_e, df_acc])
    return df_energy_date_final


#######################
# Dashboard Main Panel
st.caption("_User_")
st.subheader('Emelie Chandni Jutvik')

#######################
# SELECTED DATES
ls_dates = df_energy.groupby(['date']).count().index
selected_date = st.selectbox('Select a date', ls_dates) #date_list   

# ENERGY
df_energy_date = df_energy[df_energy['date'] == selected_date]
df_energy_plot = energy_differ(df_energy_date)
print(df_energy_date)

# ACTIVITY
df_activity = df_energy_date[df_energy_date['section'] != 'REST']

#######################

col = st.columns((5.5, 5.5), gap='medium') 
with col[0]:  
    st.markdown('#### Energy balance') 
    st.caption("_:blue[Energy inputs/outputs]_ at selected day")
    st.bar_chart(df_energy_plot, x="time", y="energy", color="label") 
    
    
with col[1]: 
    st.markdown('#### Activity')  
    st.caption("_:blue[Wearable activities]_ from selected day")
    st.bar_chart(df_energy_date, x="time", y="calorie", color="section") 
    


    