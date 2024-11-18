#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

from data.google_connection import get_calendar_data
from data.data_prepp import data_processing
from data.db_connection import write_to_db

# Write to database
# https://playground.streamlit.app/?q=data-fusion-app

#get_calendar_data()
data_processing()
write_to_db()

#######################
# Page configuration
st.set_page_config(
    page_title="IlluminateMe Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# update every 2 min
st_autorefresh(interval=2 * 60 * 1000, key="dataframerefresh")

#######################
# CSS styling
st.markdown("""
<style>

/* Remove blank space at top and bottom */ 
.block-container {
    padding-top: 0rem;
 }

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: red;
}

/* Make the toolbar transparent and the content below it clickable */ 
.st-emotion-cache-18ni7ap {
    pointer-events: none;
    background: rgb(255 255 255 / 0%)
    }
.st-emotion-cache-zq5wmm {
    pointer-events: auto;
    background: rgb(255 255 255);
    border-radius: 5px;
    }

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
    background-color: #FFFFFF;
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
df_energy = pd.read_csv('data/energy-irl-results.csv')


'''
def get_data():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")

    # Perform query.
    df_energy = conn.query('SELECT * FROM energy_balance;', ttl="10m")
    return df_energy

df_energy = get_data()
'''

#######################
# Selection functions

def bmr(weight, height, age):
    weight = 50
    height = 170
    age = 42
    BMR = int(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
    return BMR

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

def energy_at_time(df_energy_date):    
    now = datetime.now() # current date and time
    current_date = now.strftime("%Y-%m-%d")
    if df_energy_date['date'].iloc[0] < current_date:
        df_in = df_energy_date[df_energy_date['section'] == 'FOOD']
        df_out = df_energy_date[df_energy_date['section'] != 'FOOD']
        energy_in = int(sum(df_in['calorie'].values))
        energy_out = int(sum(df_out['calorie'].values))
        energy_balance = int(df_energy_date['calorie_acc'].values[-1])    
    if df_energy_date['date'].iloc[0] == current_date:
        time = now.strftime("%H:%M:%S")
        df_energy_date_balance = df_energy_date[df_energy_date['time'] <= time]
        df_in = df_energy_date_balance[df_energy_date_balance['section'] == 'FOOD']
        df_out = df_energy_date_balance[df_energy_date_balance['section'] != 'FOOD']
        energy_in = int(sum(df_in['calorie'].values))
        energy_out = int(sum(df_out['calorie'].values))
        energy_balance = int(df_energy_date_balance['calorie_acc'].values[-1])
    deficite = energy_in + energy_out
    if deficite >= 0:
        deficite_text = "+ kcal"
    else:
        deficite_text = "- kcal"
    return energy_in, energy_out, energy_balance, deficite_text

def nutrition_content(df_energy_date):
    now = datetime.now() # current date and time
    current_date = now.strftime("%Y-%m-%d")
    if df_energy_date['date'].iloc[0] < current_date:
        df_food = df_energy_date[df_energy_date['section'] == 'FOOD']       
    else:
        time = now.strftime("%H:%M:%S")
        df_food = df_energy_date[df_energy_date['time'] <= time]
        df_food = df_energy_date[df_energy_date['section'] == 'FOOD'] 
    protein_acc = sum(df_food['protein'].to_list())
    carb_acc = sum(df_food['carb'].to_list())
    fat_acc = sum(df_food['fat'].to_list())
    total_acc = sum([protein_acc, carb_acc, fat_acc])
    nutrition_acc = [protein_acc, carb_acc, fat_acc]
    nutrition_percent = [round((protein_acc/total_acc) * 100, 1) , round((carb_acc/total_acc) * 100, 1) , round((fat_acc/total_acc) * 100, 1)]
    df_nutrition_acc = pd.DataFrame({
        "label": [
            'pro', 
            'carb', 
            'fat'],
        "percent": [
            str(nutrition_percent[0]) + '%', 
            str(nutrition_percent[1]) + '%', 
            str(nutrition_percent[2]) + '%'],
        "value": nutrition_acc
    })
    return df_nutrition_acc
    
### PROTEIN
def nutrition_differ(df_energy_date):
    data_p = {
        'nutrient': df_energy_date['protein'].values,
        'time':df_energy_date['time'].values,
        'label': ['protein'] * len(df_energy_date)
        }
    df_p = pd.DataFrame(data_p)
   
    data_c = {
        'nutrient': df_energy_date['carb'].values,
        'time':df_energy_date['time'].values,
        'label': ['carb'] * len(df_energy_date)
        }
    df_c = pd.DataFrame(data_c)
    
    data_f = {
        'nutrient': df_energy_date['fat'].values,
        'time':df_energy_date['time'].values,
        'label': ['fat'] * len(df_energy_date)
        }
    df_f = pd.DataFrame(data_f)
    df_nutritions_labeled = pd.concat([df_p, df_c, df_f])
    return df_nutritions_labeled

def notes_list(df_activity): #date,time,section,distance,type,note
    df_activity = df_activity[['date', 'time', 'section', 'distance', 'type', 'note']]   
    now = datetime.now() # current date and time
    current_date = now.strftime("%Y-%m-%d")
    if df_activity['date'].iloc[0] < current_date:
        note_storage = []
        sections = df_activity['section'].values
        for i in range(0, len(sections)):
            if sections[i] == 'FOOD':
                food_string = df_activity['section'].iloc[i] + ': ' + df_activity['note'].iloc[i]
                note_storage.append(food_string)
            if sections[i] == 'WALK':
                walk_string = df_activity['section'].iloc[i] + ': ' + df_activity['distance'].iloc[i] + ' km'
                note_storage.append(walk_string)
            if sections[i] == 'SWIM':
                swim_string = df_activity['section'].iloc[i] + ': ' + df_activity['type'].iloc[i] + ' m'
                note_storage.append(swim_string)
            if sections[i] == 'RUN':
                run_string = df_activity['section'].iloc[i] + ': ' + df_activity['type'].iloc[i]
                note_storage.append(run_string)
            if sections[i] == 'BIKE':
                bike_string = df_activity['section'].iloc[i] + ': ' + df_activity['type'].iloc[i] 
                note_storage.append(bike_string)
            if sections[i] == 'STR':
                str_string = df_activity['section'].iloc[i] + ': ' + df_activity['type'].iloc[i]
                note_storage.append(str_string)           
        df_activity.insert(6, 'summary', note_storage)
        return df_activity
    if df_activity['date'].iloc[0] == current_date:
        time = now.strftime("%H:%M:%S")
        df_activity_irl = df_activity[df_activity['time'] <= time]
        note_storage = []
        sections = df_activity_irl['section'].values
        for i in range(0, len(sections)):
            if sections[i] == 'FOOD':
                food_string = df_activity_irl['section'].iloc[i] + ': ' + df_activity_irl['note'].iloc[i]
                note_storage.append(food_string)
            if sections[i] == 'WALK':
                walk_string = df_activity_irl['section'].iloc[i] + ': ' + df_activity_irl['distance'].iloc[i] + ' km'
                note_storage.append(walk_string)
            if sections[i] == 'SWIM':
                swim_string = df_activity_irl['section'].iloc[i] + ': ' + df_activity_irl['type'].iloc[i] + ' m'
                note_storage.append(swim_string)
            if sections[i] == 'RUN':
                run_string = df_activity_irl['section'].iloc[i] + ': ' + df_activity_irl['type'].iloc[i]
                note_storage.append(run_string)
            if sections[i] == 'BIKE':
                bike_string = df_activity_irl['section'].iloc[i] + ': ' + df_activity_irl['type'].iloc[i] 
                note_storage.append(bike_string)
            if sections[i] == 'STR':
                str_string = df_activity_irl['section'].iloc[i] + ': ' + df_activity_irl['type'].iloc[i]
                note_storage.append(str_string)
        df_activity_irl.insert(6, 'summary', note_storage)
        return df_activity_irl

def find_month(df_energy_date):
    current_date = df_energy_date['date'].iloc[0]
    current_month = datetime.strptime(current_date, "%Y-%m-%d").month
    text_month = ''
    if current_month == 1:
        text_month = 'January'
    if current_month == 2:
        text_month = 'February'
    if current_month == 3:
        text_month = 'Mars'
    if current_month == 4:
        text_month = 'April'
    if current_month == 5:
        text_month = 'May'
    if current_month == 6:
        text_month = 'June'
    if current_month == 7:
        text_month = 'July'
    if current_month == 8:
        text_month = 'August'
    if current_month == 9:
        text_month = 'September'
    if current_month == 10:
        text_month = 'October'
    if current_month == 11:
        text_month = 'November'
    if current_month == 12:
        text_month = 'December'
    return text_month

def find_weekday(df_energy_date):
    current_date = df_energy_date['date'].iloc[0]
    current_day = datetime.strptime(current_date, "%Y-%m-%d").weekday()
    text_day = ''
    if current_day == 0:
        text_day = 'Monday'
    if current_day == 1:
        text_day = 'Thursday'
    if current_day == 2:
        text_day = 'Wednesday'
    if current_day == 3:
        text_day = 'Turesday'
    if current_day == 4:
        text_day = 'Friday'
    if current_day == 5:
        text_day = 'Saturday'
    if current_day == 6:
        text_day = 'Sunday'
    return text_day
    
### CHART
def make_donut(source): 
    chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
        theta="value",
        color="category:N",
    )
    return chart

#######################
# Dashboard Main Panel
st.caption("_User_")
st.subheader('Emelie Chandni Jutvik')

weight = 50
height = 170
age = 42
bmr = bmr(weight, height, age)

col = st.columns((5.5, 5.5, 5.5), gap='medium') 
with col[0]:  
    
    # SELECTED DATES
    ls_dates = df_energy.groupby(['date']).count().index.values
    reverse_array = ls_dates[::-1]
    selected_date = st.selectbox('Select a date', reverse_array) #date_list   

    # ENERGY
    df_energy_date = df_energy[df_energy['date'] == selected_date]
    text_date = df_energy_date['date'].iloc[0]
    current_date = datetime.strptime(text_date, "%Y-%m-%d").day
    text_month = find_month(df_energy_date)
    text_weekday = find_weekday(df_energy_date)
    df_energy_plot = energy_differ(df_energy_date)
    energy_in, energy_out, energy_balance, deficite_text= energy_at_time(df_energy_date)
      
    # NUTRITION
    df_nutrition_acc = nutrition_content(df_energy_date)
    df_nutritions_labeled = nutrition_differ(df_energy_date)
        
    # ACTIVITY
    df_activity = df_energy_date[df_energy_date['section'] != 'REST']
    df_activity_irl = notes_list(df_activity)
    
    st.markdown('#### Energy balance') 
    st.caption("_:blue[Energy inputs/outputs]_ at selected day")
    st.bar_chart(df_energy_plot, x="time", y="energy", color="label") 
    
    st.markdown('#### Calendar notes')  
    st.caption("_:blue[Stored calendar notes]_ from selected day")
    st.dataframe(df_activity_irl,
               column_order=("time", "summary"),
               hide_index=True,
               width=600,
               column_config={
                  "time": st.column_config.TextColumn(
                      "Time",
                  ),
                  "summary": st.column_config.TextColumn(
                      "Description",
                  )}
               ) 
                        
with col[1]: 
    st.markdown('#### Date of exploration') 
    st.caption("The selected date is _:blue[" + str(current_date) + ' ' + text_month + " (" + text_weekday + ")]_")    
    
    st.markdown('#### Activity')  
    st.caption("_:blue[Stored calendar activities]_ from selected day")
    st.bar_chart(df_energy_date, x="time", y="calorie", color="section") 
    
    st.markdown('#### Daily energy balance') 
    st.caption("_:blue[Energy intake]_ at selected day")
    col1, col2, col3 = st.columns(3)
    col1.metric("Input energy", energy_in, "+ kcal")
    col2.metric("Output energy", energy_out, "-kcal")
    col3.metric("Deficite", energy_balance, deficite_text)  
    

    
with col[2]: 
    st.markdown('#### Basal metabolic rate') 
    st.caption("Your body requires _:blue[" + str(bmr) + " kcal]_ at rest")    

    st.markdown('#### Nutrition meals') 
    st.caption("_:blue[Nutrition intake]_ for registered meals at selected day")
    st.bar_chart(df_nutritions_labeled, x="time", y="nutrient", color="label") 
    
    st.markdown('#### Daily nutrition balance') 
    st.caption("_:blue[Nutrition intake]_ at selected day")    
    col1, col2, col3 = st.columns(3)
    col1.metric("Protein", str(df_nutrition_acc['value'].iloc[0]) + ' g', df_nutrition_acc['percent'].iloc[0])
    col2.metric("Carbs", str(df_nutrition_acc['value'].iloc[1]) + ' g', df_nutrition_acc['percent'].iloc[1])
    col3.metric("Fat", str(df_nutrition_acc['value'].iloc[2]) + ' g', df_nutrition_acc['percent'].iloc[2])
     

    