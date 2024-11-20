# Import libraries
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import datetime
import io
import time 

def store_in_db(data: dict):

    engine = create_engine(
        'postgresql+psycopg2://postgres:1dunSG7x@localhost:5432/energy')

     # Initialize connection.
    conn = st.connection("postgresql", type="sql")

    # Perform query.
    df_db = conn.query('SELECT * FROM activity_registration;', ttl="10m")

    print('df_db - should be empty')
    print(df_db)
   
    df_data = pd.DataFrame([data])
    df_to_db = pd.concat([df_db, df_data])
    print('Store dict to db: ')
    print(df_to_db)
    print('to database')

    # Drop old table and create new empty table
    print('Drop table from database and create a new empty table...')
    df_to_db.head(0).to_sql('activity_registration', engine, if_exists='replace',index=False)    
    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    
    print('Load data from csv...')
    df_to_db.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    #contents = output.getvalue()
    cur.copy_from(output, 'activity_registration', null='') # null values become 0
    
    print('New data was push to the database...')
    conn.commit()
    cur.close()
    conn.close()

st.header("Activity Registration")
def create_new_form():
    this_date = st.date_input("Select a date", datetime.date(2024, 11, 1))
    st.write("This is the selected date:", this_date)

    this_time = st.time_input("Select a time", value=None)
    st.write("This is the selected time", this_time)

    form = st.form(key="match", clear_on_submit=True)
    with form:
        this_activity = st.selectbox("Choose activity", ("Walk", "Run", "Swim", "Bike", "Strength"))
        this_distance = st.text_input("Distance (km)")
        this_energy = st.text_input("Energy burned (kcal)")
        this_note = st.text_input("Note")
        submit = st.form_submit_button("Submit")
        if submit:
            store_in_db({
                "date": this_date, 
                "time": this_time, 
                "activity": this_activity, 
                "distance": this_distance, 
                "energy": this_energy, 
                "note": this_note, 
                })

create_new_form()

'''

df = pd.DataFrame(
    [
       {"Food": "Havregryn"},
       {"Amount (g)": "0"},
   ]
)
edited_df = st.data_editor(df, num_rows="dynamic")
def get_data_from_db():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")

    # Perform query.
    df_energy = conn.query('SELECT * FROM energy_balance;', ttl="10m")
    return df_energy
'''
'''
df_energy = get_data_from_db()

#@st.experimental_singleton
def get_connection_to_db():
    
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    
    # Perform query.
    df_energy = conn.query('SELECT * FROM energy_balance;', ttl="10m")
    print(df_energy)
    return df_energy

conn = get_connection_to_db()
'''