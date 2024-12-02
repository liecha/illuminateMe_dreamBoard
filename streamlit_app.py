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
from data.data_dashboard import create_summary
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

# CSS styling
st.markdown("""
    <style>
    /* Remove blank space at top and bottom */ 
    .block-container {
        padding-top: 0rem;
    }

    /* breakline for metric text */
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
    overflow-wrap: break-word;
    white-space: break-spaces;
    color: red;
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
    BMR = 1360 #int(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
    df_energy = pd.read_csv('data/energy_template.csv')
    df_energy['date'] = date_new_post
    df_energy['label'] = 'REST'
    df_energy['activity'] = 'Bmr'
    df_energy['energy'] = -1 * int(BMR / 24)
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

def change_db():
    df_energy_cleaning = pd.read_csv('data/updated-database-results_clean.csv')
    df_energy_cleaning = df_energy_cleaning.drop(['energy_acc', 'protein_acc'], axis=1)
    df_energy_acc_new = calc_accumulation(df_energy_cleaning)
    df_energy_acc_new.to_csv('data/updated-database-results_clean.csv', index=False)
    #write_to_db('data/updated-database-results_clean.csv')

# RUN ONLY TO CORRECT MISTAKES IN DB
#change_db()

def day_energy(df_energy_date, bmr):
    df_output = df_energy_date[df_energy_date['label'] == 'TRAINING']
    list_output_energy = df_output['energy'].values
    sum_output = bmr
    for i in range(0, len(list_output_energy)):
        sum_output = sum_output + (-1 * list_output_energy[i])  
    return sum_output

def delete_item_from_dataset(selected_date, df_new):
    df_db = pd.read_csv('data/updated-database-results.csv')
    df_db = df_db[df_db.date != selected_date]
    df_basal_energy = basal_energy(selected_date)       
    df_new_post = df_new[df_new['date'] == selected_date]   
    df_concat = pd.concat([df_basal_energy, df_new_post]).sort_values(['time']).fillna(0) 
    df_concat = df_concat[['date', 'time', 'label', 'activity', 'distance', 'energy', 'pro', 'carb', 'fat', 'note', 'summary']]  
    df_concat_acc = calc_accumulation(df_concat)
    df_energy_new = pd.concat([df_db, df_concat_acc]).sort_values(['date', 'time'])
    df_energy_new.to_csv('data/updated-database-results.csv', index=False)

def add_new_data_to_dataset_csv(df_db_csv, df_new_post, date_new_post):
    df_new  = df_db_csv[df_db_csv['date'] == date_new_post]
    if len(df_new) == 0:
        print('Add this new day to the dataset because it is a NEW day.')
        df_basal_energy = basal_energy(date_new_post)       
        df_new_post = df_new_post[df_new_post['date'] == date_new_post]   
        df_concat = pd.concat([df_basal_energy, df_new_post]).sort_values(['time']).fillna(0) 
        df_concat = df_concat[['date', 'time', 'label', 'activity', 'distance', 'energy', 'pro', 'carb', 'fat', 'note']]  
        df_concat_acc = calc_accumulation(df_concat)
        df_energy_new = pd.concat([df_db_csv, df_concat_acc])
    else:
        print('Add this new activity ONLY because the day has already been added to the dataset.')
        df_db_csv = df_db_csv.drop(['energy_acc', 'protein_acc'], axis=1)
        df_concat_acc = pd.concat([df_db_csv, df_new_post]).sort_values(['date', 'time'])
        df_energy_new = calc_accumulation(df_concat_acc).sort_values(['date', 'time'])
    return df_energy_new

# DATABASE HANDLERS
def connect_to_db():
    # Create engine to connect to database
    engine = create_engine(
        'postgresql+psycopg2://postgres:1dunSG7x@localhost:5432/energy')
    return engine

def load_data_from_db(table_name):
    # ENERGY
    # LOADING DATA 
    # df_energy = pd.read_csv('data/updated-database-results.csv')
    conn = st.connection("postgresql", type="sql")
    df_energy = conn.query('SELECT * FROM ' + table_name + ';', ttl="10m")
    return df_energy

def store_in_db(table_name):
    engine = connect_to_db()
    df_db = pd.read_csv('data/updated-database-results.csv') 
    print('Drop table from database and create a new empty table...')
    df_db.head(0).to_sql(table_name, engine, if_exists='replace',index=False)    
    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df_db.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    cur.copy_from(output, table_name, null='') # null values become 0 
    print('New data was push to the database...')
    conn.commit()  
    cur.close()
    conn.close()

def add_registration(data: dict, table_name):
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
    
    df_db_csv = pd.read_csv('data/updated-database-results.csv') 
    df_energy_new = add_new_data_to_dataset_csv(df_db_csv, df_new_post, date_new_post)    
    df_energy_new.to_csv('data/updated-database-results.csv', index=False)
    print('Result uploaded in csv-file...')
    store_in_db(table_name)
    print('Result uploaded in database...')
    st.rerun()

# Update every 1 min
#st_autorefresh(interval=1 * 60 * 1000, key="dataframerefresh")
df_energy =  df_db_csv = pd.read_csv('data/updated-database-results.csv') #load_data_from_db('energy_balance')

def build_dashboard(df_energy):
    bmr = 1360 #bmr(50, 170, 42)
    date_now, time_now =  date_time_now()   
    selected_date = st.date_input("Select a date", date_now, key='head_selector')

    selected_date, selected_time = datetime_to_string(selected_date, time_now)
    current_date, text_month, text_weekday = text_dates(selected_date)

    #df_energy = load_data_from_db('energy_balance')
    df_energy_date = df_energy[df_energy['date'] == selected_date]
    sum_energy_output = day_energy(df_energy_date, bmr)
    col = st.columns((5.5, 5.5, 5.5), gap='medium') 
    with col[0]:                    
        if len(df_energy_date) == 0:
            st.markdown('#### Date of exploration') 
            st.caption("The selected date is _:blue[" + str(current_date) + ' ' + text_month + " (" + text_weekday + ")]_")      
        else:
            st.markdown('#### Date of exploration') 
            st.caption("The selected date is _:blue[" + str(current_date) + ' ' + text_month + " (" + text_weekday + ")]_")               
            st.markdown('#### Overview') 
            st.caption("_:blue[Energy inputs/outputs]_ at selected day")
            
            # NUTRITION
            df_nutrition_acc = nutrition_content(df_energy_date)
            df_nutritions_labeled = nutrition_differ(df_energy_date)
                
            # ACTIVITY
            df_activity = df_energy_date[df_energy_date['label'] != 'REST']
            df_activity_irl = notes_list(df_activity)
            
            df_energy_plot = energy_differ(df_energy_date)
            energy_in, energy_out, energy_balance, deficite_text = energy_at_time(df_energy_date)
            st.bar_chart(df_energy_plot, x="time", y="energy", color="label") 
            
            st.markdown('#### Registration list')  
            st.caption("_:blue[Stored registrations]_ from selected day in _:blue[real time]_")
            if len(df_energy_date) > 0:
                row_insert = len(df_activity_irl) * [False]
                df_activity_irl.insert(0, 'delete', row_insert)
                df_activity_show = df_activity_irl[['delete', 'time', 'summary']]
                edited_df = st.data_editor(
                    df_activity_show, 
                    column_config={
                        "time": st.column_config.Column(
                            "Time",
                            width="small",
                            required=True,
                        ),
                        "summary": st.column_config.Column(
                            "Summary",
                            width="large",
                            required=True,
                        ),
                        "delete": st.column_config.Column(
                            "Delete",
                            width="small",
                            required=True,
                        ),
                    },
                    key='change_registration', 
                    hide_index=True, 
                    use_container_width=True)

                button_pressed = st.button("Delete item")
                if button_pressed:
                    df_drop = edited_df[edited_df.delete == True]
                    print(df_drop)
                    for i in range(0, len(df_drop)):
                        drop_time = df_drop['time'].iloc[i]
                        drop_summary = df_drop['summary'].iloc[i]
                        for j in range(0, len(df_activity_irl)):
                            df_acrtivity_time = df_activity_irl['time'].iloc[j]
                            df_acrtivity_summary = df_activity_irl['summary'].iloc[j]
                            if (df_acrtivity_time == drop_time) and (df_acrtivity_summary == drop_summary):
                                df_activity_irl = df_activity_irl[df_activity_irl['time'] != drop_time]
                                break
                    df_new = df_activity_irl.drop(['delete'], axis=1)
                    delete_item_from_dataset(selected_date, df_new)
                    button_pressed = False
                    st.write("Changes where saved...")  
                            
    with col[1]:
        if len(df_energy_date) == 0:
            st.markdown('#### Basal metabolic rate') 
            st.caption("Your body requires _:blue[" + str(bmr) + " kcal]_ at rest")
            
            st.markdown('#### Activity')  
            st.caption("There is _:blue[no data available]_ for the selected day")

            st.markdown('#### Current energy balance') 
            st.caption("There is _:blue[no data available]_ for the selected day")
        else:
            st.markdown('#### Basal metabolic rate') 
            st.caption("Your body requires _:blue[" + str(bmr) + " kcal]_ at rest")
            
            st.markdown('#### Activity')  
            st.caption("_:blue[Stored calendar activities]_ from selected day in _:blue[real time]_")
            st.bar_chart(df_energy_date, x="time", y="energy", color="activity") 
            
            st.markdown('#### Current energy balance') 
            st.caption("_:blue[Energy intake]_ at selected day in _:blue[real time]_")
            col1, col2, col3 = st.columns(3)
            col1.metric("Input energy", energy_in, "+ kcal")
            col2.metric("Output energy", energy_out, "-kcal")
            col3.metric("Deficite", energy_balance, deficite_text)  
        
    with col[2]: 
        if len(df_energy_date) == 0:
            st.markdown('#### Total energy output') 
            st.caption("_:blue[Total energy needed]_ at selected day is _:blue[" + str(int(sum_energy_output)) + " kcal]_")  
            
            st.markdown('#### Nutrition meals') 
            st.caption("There is _:blue[no data available]_ for the selected day")

            st.markdown('#### Current nutrition balance') 
            st.caption("There is _:blue[no data available]_ for the selected day")
        else:
            st.markdown('#### Total energy output') 
            st.caption("_:blue[Total energy needed]_ at selected day is _:blue[" + str(int(sum_energy_output)) + " kcal]_")  

            st.markdown('#### Nutrition meals') 
            if sum(df_nutritions_labeled['nutrient'].values) == 0.0:
                st.caption("There are _:blue[no meals registered]_ for the selected day")
                
            else:
                st.caption("_:blue[Nutrition intake]_ for registered meals at selected day")
                st.bar_chart(df_nutritions_labeled, x="time", y="nutrient", color="label") 
            
            st.markdown('#### Current nutrition balance') 
            if sum(df_nutritions_labeled['nutrient'].values) == 0.0:
                st.caption("There are _:blue[no meals registered]_ for the selected day")
            else:
                st.caption("_:blue[Nutrition intake]_ at selected day in _:blue[real time]_")    
                col1, col2, col3 = st.columns(3)
                col1.metric("Protein", str(df_nutrition_acc['value'].iloc[0]) + ' g', df_nutrition_acc['percent'].iloc[0])
                col2.metric("Carbs", str(df_nutrition_acc['value'].iloc[1]) + ' g', df_nutrition_acc['percent'].iloc[1])
                col3.metric("Fat", str(df_nutrition_acc['value'].iloc[2]) + ' g', df_nutrition_acc['percent'].iloc[2])  

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
    form_activity = st.form(key="activity", clear_on_submit=True)
    with form_activity:
        this_activity = st.selectbox("Choose activity", ("","Walk", "Run", "Swim", "Bike", "Strength"))
        this_distance = st.text_input("Distance (km)")
        this_energy = st.text_input("Energy burned (kcal)")
        this_note = st.text_input("Details")
        submit_activity = st.form_submit_button("Submit")
        if submit_activity:
            add_registration(
                {     
                    "date": this_date, 
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
    form_food = st.form(key="form_create_meal", clear_on_submit=True)
    with form_food:
        this_code = st.text_input("Meal code (kcal/pro/carb/fat)", code)
        food_split = this_code.split('/')
        this_note = st.text_input("Details", options)
        submit_food = st.form_submit_button("Submit")    
        if submit_food:
            add_registration(
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
    form_recipie = st.form(key="form_add_meal", clear_on_submit=True)
    with form_recipie:
        this_name = st.text_input("Name of recipie")
        st.text_input("Meal code (kcal/pro/carb/fat)", code)
        save_favorite = st.checkbox("⭐️ Save recipie as favorite ")
        submit_recipie = st.form_submit_button("Save recipie")    
        if submit_recipie:
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

def create_form_add_food_item():
    form_food_item = st.form(key="form_add_food_item", clear_on_submit=True)
    with form_food_item:
        this_name = st.text_input("Name of food item", key='this_name')
        this_energy = st.text_input("Energy (kcal / 100 g)", key='this_energy')
        this_pro = st.text_input("Proteins (g / 100 g)",  key='this_pro')
        this_carb = st.text_input("Carbohydrates (g / 100 g)",  key='this_carb')
        this_fat = st.text_input("Fats (g / 100 g)",  key='this_fat')
        submit_food_item = st.form_submit_button("Save food item")    
        if submit_food_item:
            new_food_item = {
                'livsmedel': this_name,
                'calorie': this_energy,
                'protein': this_pro,
                'carb': this_carb,
                'fat': this_fat
            }
            df_new_food_item = pd.DataFrame([new_food_item])
            df_food_db = pd.read_csv('data/livsmedelsdatabas.csv')
            df_add_food_item = pd.concat([df_food_db, df_new_food_item])
            df_add_food_item.to_csv('data/livsmedelsdatabas.csv', index=False)


st.caption("_User_")
st.subheader('Emelie Chandni Jutvik')

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "🏃🏽‍♀️ Activity Registration", 
    "🍲 Meal Registration",
    "📝 Recipies",
    "🗄️ Database",
    ])
with tab1:
    build_dashboard(df_energy)
    
with tab2:
    col = st.columns((5.5, 5.5), gap='medium') 
    with col[0]:  
        st.header("Activity Registration")
        create_new_form_activity()

with tab3:
    col = st.columns((5.5, 5.5), gap='medium') 
    with col[0]: 
        st.header("Add recipie")
        st.caption("Type in a _:blue[ recipie name]_ that you want to add to your meal")  
        df_recipie_db = pd.read_csv('data/meal_databas.csv').sort_values(['name'])
        recipie_list = df_recipie_db['name'].unique()
        options_recipie = st.multiselect(
            "Select recipies to add to your meal",
            recipie_list,
            key='find_recipie'
        )
       
        st.header("Add food items")
        st.caption("_:blue[Type in food items]_ that you want to add to your meal")  
        df_food_db = pd.read_csv('data/livsmedelsdatabas.csv')
        food_list = df_food_db['livsmedel'].values
        options = st.multiselect(
            "Select food items to add to your meal",
            food_list,
            key='create_meal'
        )

        st.header("Your meal")
        st.caption("This is the _:blue[ content of your meal]_")  
        temp_store = []
        code = ''
        options_string = ''
        df_recipies = pd.DataFrame([{"Food":'Deleted', "Amount (g)": 0.0}])
        df_meal = pd.DataFrame([{"Food":'', "Amount (g)": 0.0}])
        if (len(options) > 0) or len(options_recipie):
            temp_store_recipies = []
            if len(options_recipie) > 0:
                for i in range(0, len(options_recipie)):
                    df_this_recpie = df_recipie_db[df_recipie_db['name'] == options_recipie[i]]
                    for k in range(0, len(df_this_recpie)):
                        temp_store_recipies.append({
                            "Food": df_this_recpie['livsmedel'].iloc[k], 
                            "Amount (g)": df_this_recpie['amount'].iloc[k]})
                    options_string = options_string + df_this_recpie['name'].iloc[0] + '/'
                df_recipies = pd.DataFrame(temp_store_recipies)
            for i in range(0, len(options)):
                temp_store.append({"Food": options[i], "Amount (g)": 0})
                options_string = options_string + options[i] + '/'
            df_meal = pd.DataFrame(temp_store)
            df_total = pd.concat([df_recipies, df_meal])
            df_total = df_total[df_total['Food'] != 'Deleted']
            df_result_meal = st.data_editor(df_total, key='create_meal_editor', hide_index=True, use_container_width=True)
            print(options_string)
            if len(df_result_meal) > 0:
                df_food_nutrition = locate_eatables(df_result_meal)
                code = code_detector(df_result_meal, df_food_nutrition)
                df_result_meal['code'] = code
        else:
            st.error('Your meal is empty', icon="🚨")
            st.write('Serach for food items to add to your meal.')

    with col[1]:  
        st.header("Food Registration")
        st.caption("_:blue[Register your meal]_ to the dashboard")  
        options_string = options_string[:-1]
        create_new_form_food(code, options_string)

with tab4:
    col = st.columns((5.0, 5.0, 5.0), gap='medium') 
    with col[0]: 
        st.header("Recipies in database")
        st.caption("These are the stored _:blue[ recipies in your database]_")  
        df_meal_db = pd.read_csv('data/meal_databas.csv')
        summary = df_meal_db.groupby(['name', 'code']).count().sort_values(['favorite', 'name'])
        for i in range(0, len(summary)):
            this_key = 'meal_' + str(i)
            this_meal = df_meal_db[df_meal_db['name'] == summary.index[i][0]]
            if this_meal['favorite'].iloc[0] == True:
                this_icon = '⭐️'
            else:
                this_icon = '🍲'
            expander = st.expander(summary.index[i][0], icon=this_icon)
            this_code = this_meal['code'].iloc[0]
            expander.write("_**Meal code**_: :green[" + this_code + "]")
            expander.write("_**Ingredients:**_ \n")
            for j in range(0, len(this_meal)):
                expander.write(':violet[' + "     -- " + this_meal['livsmedel'].iloc[j] + ' ] ' +  '   (_' + str(this_meal['amount'].iloc[j])+ "_ g)") 

with tab5:
    col = st.columns((5.0, 5.0, 5.0), gap='medium') 
    with col[0]: 
        st.header("Add food item")
        st.caption("_:blue[Add new food item]_ to the database")  
        create_form_add_food_item()
    with col[1]: 
        st.header("Search for food items")
        st.caption("_:blue[Type in food items]_ that you want to add to your recipie")  
        df_food_db = pd.read_csv('data/livsmedelsdatabas.csv')
        food_list = df_food_db['livsmedel'].values
        options = st.multiselect(
            "Select food items to your recipie",
            food_list,
            key='add_meal'
        )
        
        st.header("Create recipie")
        st.caption("This is the _:blue[ content of your recipie]_")  
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
            st.error('Your recipie is empty', icon="🚨")
            st.write('Serach for food items to add to your recipie.')
    with col[2]:
        st.header("Save recipie")
        st.caption("_:blue[Save your recipie]_ to the database")  
        create_form_add_meal(meal_df)         