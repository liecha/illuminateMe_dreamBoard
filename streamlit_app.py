# Import libraries
import streamlit as st
import pandas as pd
import datetime
import altair as alt
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine
import io

from data.data_prepp import data_processing
from data.db_connection import write_to_db


from data.data_dashboard import date_time_now
from data.data_dashboard import datetime_to_string
from data.data_dashboard import text_dates
from data.data_dashboard import energy_differ
from data.data_dashboard import energy_at_time
from data.data_dashboard import nutrition_content
from data.data_dashboard import nutrition_differ
from data.data_dashboard import notes_list
from data.data_dashboard import find_month
from data.data_dashboard import find_weekday

from data.nutritions import locate_eatables
from data.nutritions import code_detector

# Page configuration
st.set_page_config(
    page_title="IlluminateMe Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# update every 2 min
#st_autorefresh(interval=2 * 60 * 1000, key="dataframerefresh")
data_processing()
write_to_db()

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

div[data-testid="InputInstructions"] > span:nth-child(1) {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# Load data
df_energy = pd.read_csv('data/energy-irl-results.csv')

# CONSTANTS
def bmr(weight, height, age):
    weight = 50
    height = 170
    age = 42
    BMR = int(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
    return BMR

def basal_energy(date_new_post):
    weight = 50
    height = 170
    age = 42
    BMR = int(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
    df_energy = pd.read_csv('data/energy_template.csv')
    df_energy['date'] = date_new_post
    df_energy['label'] = 'REST'
    df_energy['activity'] = 'Bmr'
    df_energy['energy'] = -1 * (BMR / 24)
    return df_energy

def calc_accumulation(df_data):
    ls_dates = df_data.groupby(['date']).count().index.to_list()
    storage = []
    for j in range(0, len(ls_dates)):
        df_day = df_data[df_data['date'] == ls_dates[j]]
        ls_calories = df_day['energy'].values
        ls_protein = df_day['pro'].values
        ls_acc_calories = [ls_calories[0]]
        ls_acc_protein = [ls_protein[0]]
        for i in range(0, len(ls_calories) - 1):           
            counting_calories = ls_acc_calories[i] + ls_calories[i + 1]
            counting_protein = ls_acc_protein[i] + ls_protein[i + 1]
            ls_acc_calories.append(counting_calories) 
            ls_acc_protein.append(counting_protein)
        df_day.insert(6, 'energy_acc', ls_acc_calories)
        df_day.insert(8, 'protein_acc', ls_acc_protein)
        storage.append(df_day)
    df_energy_acc = pd.concat(storage)
    return df_energy_acc

# WRITE TO DATABASE
def store_in_db(data: dict, table_name):
    df_registration = pd.DataFrame([data])
    this_date = df_registration['date'].iloc[0]
    this_time = df_registration['time'].iloc[0]
    date_str, time_str = datetime_to_string(this_date, this_time)
    new_data = {
        'date': date_str,
        'time': time_str,
        'label': df_registration['label'].iloc[0],
        'energy': df_registration['energy'].iloc[0],
        'pro': df_registration['pro'].iloc[0],
        'carb': df_registration['carb'].iloc[0],
        'fat': df_registration['fat'].iloc[0],
        'activity': df_registration['activity'].iloc[0],
        'distance': df_registration['distance'].iloc[0],
        'note': df_registration['note'].iloc[0]
    }
    df_new_post = pd.DataFrame([new_data])
    df_new_post.to_csv('data/new-post-results.csv', index=False)
    date_new_post = df_new_post['date'].iloc[0]
    
    # Create engine to connect to database
    engine = create_engine(
        'postgresql+psycopg2://postgres:1dunSG7x@localhost:5432/energy')

     # Initialize connection
    conn = st.connection("postgresql", type="sql")
    df_db = conn.query('SELECT * FROM ' + table_name + ';', ttl="10m")
    
    df_test = df_db[df_db['date'] == date_new_post]
    if len(df_test) == 0:
        print('Add this new day to the dataset because it is a NEW day.')
        df_basal_energy = basal_energy(date_new_post)       
        df_new_post = df_new_post[df_new_post['date'] == date_new_post]   
        df_concat = pd.concat([df_basal_energy, df_new_post]).sort_values(['time']).fillna(0) 
        df_concat = df_concat[['date', 'time', 'label', 'activity', 'distance', 'energy', 'pro', 'carb', 'fat', 'note']]  
        df_concat_acc = calc_accumulation(df_concat)
        df_energy_new = pd.concat([df_db, df_concat_acc])
    else:
        print('Add this new activity ONLY because the day has already been added to the dataset.')
        df_db = df_db.drop(['energy_acc', 'protein_acc'], axis=1)
        df_concat_acc = pd.concat([df_db, df_new_post]).sort_values(['date', 'time'])
        df_energy_new = calc_accumulation(df_concat_acc).sort_values(['date', 'time'])
      
    df_energy_new.to_csv('data/updated-database-results.csv', index=False)
    print('Result uploaded in csv-database...')

    # Drop old table and create new empty table
    print('Drop table from database and create a new empty table...')
    df_energy_new.head(0).to_sql(table_name, engine, if_exists='replace',index=False)    
    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df_energy_new.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    #contents = output.getvalue() 
    cur.copy_from(output, table_name, null='') # null values become 0 
    print('New data was push to the database...')
    conn.commit()  
    cur.close()
    conn.close()

### ACTIVITY REGISTRATION
def create_new_form_activity():
    date_now, time_now =  date_time_now()   
    col = st.columns((2.5, 2.5), gap='medium') 
    with col[0]:  
        this_date = st.date_input("Select a date", date_now, key="act")
        st.write("Selected date: ", this_date)
    with col[1]: 
        this_time = st.time_input("Select a time", value=None, key="act_time")
        st.write("Selected time: ", this_time)
    form = st.form(key="activity", clear_on_submit=True)
    with form:
        this_activity = st.selectbox("Choose activity", ("","Walk", "Run", "Swim", "Bike", "Strength"))
        this_distance = st.text_input("Distance (km)")
        this_energy = st.text_input("Energy burned (kcal)")
        this_note = st.text_input("Details")
        submit = st.form_submit_button("Submit")
        if submit:
            store_in_db(
                {     
                    "date": date_now, 
                    "time": this_time,
                    "label": 'TRAINING', 
                    "energy": -1 * int(this_energy), 
                    "pro": 0, 
                    "carb": 0, 
                    "fat": 0, 
                    "activity": this_activity, 
                    "distance": this_distance,                
                    "note": str(this_note), 
                },
                    'energy_balance'
                )
            
### FOOD REGISTRATION
def create_new_form_food(code, options):
    date_now, time_now =  date_time_now() 
    col = st.columns((2.5, 2.5), gap='medium') 
    with col[0]:  
        this_date = st.date_input("Select a date", date_now, key="foo_date")
        st.write("Selected date: ", this_date)
    with col[1]: 
        this_time = st.time_input("Select a time", value=None, key="foo_time")
        st.write("Selected time: ", this_time)
    form = st.form(key="food", clear_on_submit=True)
    with form:
        this_code = st.text_input("Food code (kcal/pro/carb/fat)", code)
        food_split = this_code.split('/')
        this_note = st.text_input("Details", options)
        submit = st.form_submit_button("Submit")    
        if submit:
            # date,time,label,energy,pro,carb,fat,note
            # date,time,label,energy,protein,activity,distance,note
            store_in_db(
                {
                    "date": this_date, 
                    "time": this_time,
                    "label": 'FOOD', 
                    "energy": int(food_split[0]),
                    "pro": int(food_split[1]),
                    "carb": int(food_split[1]),
                    "fat": int(food_split[3]),
                    "activity": 'Eat', 
                    "distance": 0.0, 
                    "note": str(this_note), 
                },
                    'energy_balance'
                )

# DATA HANDLER
# SELECTED DATES
ls_dates = df_energy.groupby(['date']).count().index.values
reverse_array = ls_dates[::-1]

# DASHBOARD
weight = 50
height = 170
age = 42
bmr = bmr(weight, height, age)

st.caption("_User_")
st.subheader('Emelie Chandni Jutvik')
tab1, tab2, tab3, tab5 = st.tabs([
    "Dashboard",
    "Activity Registration", 
    "Food Registration", 
    "Stored meals"
    ])
with tab1:
    col = st.columns((5.5, 5.5, 5.5), gap='medium') 
    with col[0]:        
        # SELECTED DATES
        selected_date = st.selectbox('Select a date', reverse_array)  

        # ENERGY
        df_energy_date = df_energy[df_energy['date'] == selected_date]
        current_date, text_month, text_weekday = text_dates(df_energy_date)
        df_energy_plot = energy_differ(df_energy_date)
        energy_in, energy_out, energy_balance, deficite_text = energy_at_time(df_energy_date)
          
        # NUTRITION
        df_nutrition_acc = nutrition_content(df_energy_date)
        df_nutritions_labeled = nutrition_differ(df_energy_date)
            
        # ACTIVITY
        df_activity = df_energy_date[df_energy_date['label'] != 'REST']
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
        st.bar_chart(df_energy_date, x="time", y="energy", color="activity") 
        
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

with tab2:
    col = st.columns((5.5, 5.5), gap='medium') 
    with col[0]:  
        st.header("Activity Registration")
        create_new_form_activity()

with tab3:
    col = st.columns((5.5, 5.5), gap='medium') 
    with col[0]:  
        st.header("Create Food Code")
        df_food_db = pd.read_csv('data/livsmedelsdatabas.csv')
        food_list = df_food_db['livsmedel'].values
        options = st.multiselect(
            "Select foods in your meal",
            food_list,
            ["Havregryn fullkorn"]
        )
        st.caption("This is the _:blue[ content of your meal]_")  
        temp_store = []
        options_string = ''
        for i in range(0, len(options)):
            temp_store.append({"Food": options[i], "Amount (g)": 0})
            options_string = options_string + options[i] + '/'
        df = pd.DataFrame(temp_store)
        edited_df = st.data_editor(df, hide_index=True, use_container_width=True)
        if len(edited_df) > 0:
            df_food_nutrition = locate_eatables(edited_df)
            code = code_detector(edited_df, df_food_nutrition)
            st.write("FOOD CODE: ", code)
    with col[1]:
        st.header("Food Registration")
        create_new_form_food(code, options_string)

with tab5:
    col = st.columns((4.5, 6.5), gap='medium') 
    with col[0]:  
        st.header("Meals in database")
        df_meal_db = pd.read_csv('data/meal_databas.csv')
        summary = df_meal_db.groupby(['name', 'code']).count()
        for i in range(0, len(summary)):
            expander = st.expander(summary.index[i][0])
            this_meal = df_meal_db[df_meal_db['name'] == summary.index[i][0]]
            this_code = this_meal['code'].iloc[0]
            store_strings = ["_**Ingredients:**_ \n\n"]
            for j in range(0, len(this_meal)):
                store_strings.append(':violet[' + this_meal['livsmedel'].iloc[j] + ' ] ' +  str(this_meal['amount'].iloc[j]) + " g\n\n")
            concat_string = "\n\n" + rf""
            for k in range(0, len(store_strings)):
                concat_string = concat_string + store_strings[k]
            expander.write(rf""" 
                                {"_**Meal code**_: :green[" + this_code + "]"}
                                {concat_string}
                            """)
    