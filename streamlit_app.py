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

#data_processing()
#write_to_db()
#Protein 30% - 35% 
#Fat 20% - 25% 
#Carbs 50% - 65% 

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

# CONSTANTS
def bmr(weight, height, age):
    weight = 50
    height = 170
    age = 42
    BMR = 1360 #int(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
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
        this_time = st.time_input("What time did you eat", value=None, key="foo_time")
        st.write("Selected time: ", this_time)
    form = st.form(key="form_create_meal", clear_on_submit=True)
    with form:
        this_code = st.text_input("Food code (kcal/pro/carb/fat)", code)
        food_split = this_code.split('/')
        this_note = st.text_input("Details", options)
        submit = st.form_submit_button("Submit")    
        if submit:
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
def create_form_add_meal(meal_df):
    form = st.form(key="form_add_meal", clear_on_submit=True)
    with form:
        this_name = st.text_input("Name of meal")
        st.text_input("Food code (kcal/pro/carb/fat)", code)
        save_favorite = st.checkbox("⭐️ Save meal as favorite ")
        submit = st.form_submit_button("Save meal")    
        if submit:
            df_meal_db = pd.read_csv('data/meal_databas.csv')
            if save_favorite == True:
                meal_df['favorite'] = True
            else:  
                meal_df['favorite'] = False
            meal_df['name'] = this_name
            meal_df = meal_df.rename(columns={"Food": "livsmedel", "Amount (g)": "amount"})
            meal_df = meal_df[['name', 'livsmedel' , 'amount', 'code', 'favorite']]
            add_meal = pd.concat([df_meal_db, meal_df])
            add_meal.to_csv('data/meal_databas.csv', index=False)

# DATA HANDLER
# DASHBOARD
weight = 50
height = 170
age = 42
bmr = bmr(weight, height, age)

st.caption("_User_")
st.subheader('Emelie Chandni Jutvik')
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "🏃🏽‍♀️ Activity Registration", 
    "🍛 Meal Registration",
    "🗄️ Add meal to database"
    ])
with tab1:
    col = st.columns((5.5, 5.5, 5.5), gap='medium') 
    with col[0]:        
        # SELECTED DATES
        date_now, time_now =  date_time_now()   
        selected_date = st.date_input("Select a date", date_now, key="head_selector")
        selected_date, selected_time = datetime_to_string(selected_date, time_now)
        current_date, text_month, text_weekday = text_dates(selected_date)
        
        # ENERGY
        # LOADING DATA
        #df_energy = pd.read_csv('data/energy-irl-results.csv')
        
        # Update every 2 min
        st_autorefresh(interval=2 * 60 * 1000, key="dataframerefresh")
        # Initialize connection.
        conn = st.connection("postgresql", type="sql")
        # Perform query.
        df_energy = conn.query('SELECT * FROM energy_balance;', ttl="10m")
        df_energy_date = df_energy[df_energy['date'] == selected_date]
        if len(df_energy_date) == 0:
            st.markdown('#### Energy balance') 
            st.caption("There is _:blue[no data available]_ for the selected day")
        else:            
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
        if len(df_energy_date) == 0:
            st.markdown('#### Date of exploration') 
            st.caption("The selected date is _:blue[" + str(current_date) + ' ' + text_month + " (" + text_weekday + ")]_")   
            
            st.markdown('#### Activity')  
            st.caption("There is _:blue[no data available]_ for the selected day")

            st.markdown('#### Daily energy balance') 
            st.caption("There is _:blue[no data available]_ for the selected day")
        else:
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
        if len(df_energy_date) == 0:
            st.markdown('#### Basal metabolic rate') 
            st.caption("Your body requires _:blue[" + str(bmr) + " kcal]_ at rest")
            
            st.markdown('#### Nutrition meals') 
            st.caption("There is _:blue[no data available]_ for the selected day")

            st.markdown('#### Daily nutrition balance') 
            st.caption("There is _:blue[no data available]_ for the selected day")
        else:
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
    col = st.columns((5.0, 5.0, 5.0), gap='medium') 
    with col[0]:  
        st.header("Search for food")
        st.caption("_:blue[Type in food]_ that you want to add to your meal")  
        df_food_db = pd.read_csv('data/livsmedelsdatabas.csv')
        food_list = df_food_db['livsmedel'].values
        options = st.multiselect(
            "Select foods to your meal",
            food_list,
            key='create_meal'
        )
        st.header("Stored meals")
        st.caption("These are the stored _:blue[ meals in your database]_")  
        df_meal_db = pd.read_csv('data/meal_databas.csv')
        summary = df_meal_db.groupby(['name', 'code']).count().sort_values(['favorite', 'name'])
        for i in range(0, len(summary)):
            this_key = 'meal_' + str(i)
            this_meal = df_meal_db[df_meal_db['name'] == summary.index[i][0]]
            if this_meal['favorite'].iloc[0] == True:
                this_icon = '⭐️'
            else:
                this_icon = '🍛'
            expander = st.expander(summary.index[i][0], icon=this_icon)
            this_code = this_meal['code'].iloc[0]
            expander.write("_**Meal code**_: :green[" + this_code + "]")
            expander.write("_**Ingredients:**_ \n")
            for j in range(0, len(this_meal)):
                expander.write(':violet[' + "     -- " + this_meal['livsmedel'].iloc[j] + ' ] ' +  '   (_' + str(this_meal['amount'].iloc[j])+ "_ g)")
    with col[1]:  
        st.header("Your meal")
        st.caption("This is the _:blue[ content of your meal]_")  
        temp_store = []
        code = ''
        options_string = ''
        if len(options) > 0:
            options_string = ''
            for i in range(0, len(options)):
                temp_store.append({"Food": options[i], "Amount (g)": 0})
                options_string = options_string + options[i] + '/'
            df = pd.DataFrame(temp_store)
            meal_df = st.data_editor(df, key='create_meal_editor', hide_index=True, use_container_width=True)
            if len(meal_df) > 0:
                df_food_nutrition = locate_eatables(meal_df)
                code = code_detector(meal_df, df_food_nutrition)
                meal_df['code'] = code
        else:
            st.write('Your meal is empty. Serach for foods to add to your meal.')
    with col[2]:
        st.header("Food Registration")
        st.caption("_:blue[Register your meal]_ to the dashboard")  
        create_new_form_food(code, options_string)

with tab4:
    col = st.columns((5.0, 5.0, 5.0), gap='medium') 
    with col[0]: 
        st.header("Search for food")
        st.caption("_:blue[Type in food]_ that you want to add to your meal")  
        df_food_db = pd.read_csv('data/livsmedelsdatabas.csv')
        food_list = df_food_db['livsmedel'].values
        options = st.multiselect(
            "Select foods to your meal",
            food_list,
            key='add_meal'
        )
        st.header("Meals in database")
        st.caption("These are the stored _:blue[ meals in your database]_")  
        df_meal_db = pd.read_csv('data/meal_databas.csv')
        summary = df_meal_db.groupby(['name', 'code']).count().sort_values(['favorite', 'name'])
        for i in range(0, len(summary)):
            this_key = 'meal_' + str(i)
            this_meal = df_meal_db[df_meal_db['name'] == summary.index[i][0]]
            if this_meal['favorite'].iloc[0] == True:
                this_icon = '⭐️'
            else:
                this_icon = '🍛'
            expander = st.expander(summary.index[i][0], icon=this_icon)
            this_code = this_meal['code'].iloc[0]
            expander.write("_**Meal code**_: :green[" + this_code + "]")
            expander.write("_**Ingredients:**_ \n")
            for j in range(0, len(this_meal)):
                expander.write(':violet[' + "     -- " + this_meal['livsmedel'].iloc[j] + ' ] ' +  '   (_' + str(this_meal['amount'].iloc[j])+ "_ g)") 
    with col[1]: 
        st.header("Create meal")
        st.caption("This is the _:blue[ content of your meal]_")  
        temp_store = []
        code = ''
        meal_df = pd.DataFrame([{}])
        if len(options) > 0:
            for i in range(0, len(options)):
                temp_store.append({"Food": options[i], "Amount (g)": 0})
            df_my = pd.DataFrame(temp_store)
            meal_df = st.data_editor(df_my, key='add_meal_editor', hide_index=True, use_container_width=True)
            if len(meal_df) > 0:
                df_food_nutrition = locate_eatables(meal_df)
                code = code_detector(meal_df, df_food_nutrition)
                meal_df['code'] = code
        else:
            st.error('Your meal is empty', icon="🚨")
            st.write('Serach for foods to add to your meal.')
    with col[2]:
        st.header("Save meal")
        st.caption("_:blue[Save your meal]_ to the database")  
        create_form_add_meal(meal_df)
        