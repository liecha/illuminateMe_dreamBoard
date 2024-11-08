#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt

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
df_results = pd.read_csv('data/ai-model/ai-model-results-smooth.csv')
df_sports = pd.read_csv('data/wearable/sports-results.csv')
df_sleep = pd.read_csv('data/wearable/sleep-results.csv')
df_calendar = pd.read_csv('data/calendar/calendar-results.csv')
df_notes = pd.read_csv('data/notes/note-results.csv')

df_energy = pd.read_csv('data/energy-results.csv')
#######################
# Selection functions

### GENERAL
def date_to_text(df_results, date_list):
    date_text_list = []
    for i in range(0, len(date_list)):
        this_date = df_results[df_results['date'] == date_list[i]] 
        date_text = this_date.iloc[0]['date_in_text']
        date_text_list.append(date_text)
    return date_text_list

def weekday_summary_peaks(df_results):
    result_score_10 = df_results[df_results['score_smooth'] >= 8]
    date_list_score = result_score_10.groupby(['date']).count()    
    date_list_score['date'] = date_list_score.index
    date_text = date_to_text(result_score_10, date_list_score['date'].values)
    date_list_score.insert(0, 'Day/Month/Weekday', date_text)
    date_list_score = date_list_score[['date', 'Day/Month/Weekday', 'Stress score']]
    date_list_score.rename(columns={"Stress score": "Counted stress peaks"}, inplace = True)
    return date_list_score

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

### CALENDAR
def calendar_selection(df_calendar, selected_date):
    df_calendar_date = df_calendar[df_calendar['date'] == selected_date]    
    if len(df_calendar_date) == 0:
        data = {
            'event': ['No events where registered at this date']
            }
        df_calendar_date = pd.DataFrame(data)     
    else:
        df_calendar_date = df_calendar_date.sort_values(by=['time'])
    return df_calendar_date

def note_selection(df_notes, selected_date):
    df_notes_date = df_notes[df_notes['date'] == selected_date]    
    if len(df_notes_date) == 0:
        data = {
            'note': ['No notes where made at this date']
            }
        df_notes_date = pd.DataFrame(data)      
    else:
        df_notes_date = df_notes_date.sort_values(by=['time'])
    return df_notes_date

def calendar_popdown(df_date_score):
    list_of_peaks = []
    for i in range(0, len(df_date_score)):
        date_string = df_date_score.iloc[i]['date']
        time_string = df_date_score.iloc[i]['time']
        result_string = date_string + ' at ' + time_string
        list_of_peaks.append(result_string)
    return list_of_peaks

def clear_text():
    st.session_state.my_text = st.session_state.widget
    st.session_state.widget = ""

#######################
# Plots

# Line plit
def make_lineplot(input_df, input_y, input_x):   
    line_plot = alt.Chart(input_df).mark_line().encode(
        x=input_x, # time
        y=input_y # score
    )
    return line_plot

# Barplot
def make_barplot(input_df, input_y, input_x):    
    barplot = alt.Chart(input_df).mark_bar().encode(
            x=input_x, #'labels',
            y=input_y, #'sportTime(s)'
        ) 
    return barplot

# Donut chart
def make_donut(source):    
    donut_chart =  alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="value",
        color="category:N",
    ).properties(width=130, height=130)
    return donut_chart

#######################
# Dashboard Main Panel
st.caption("_User_")
st.subheader('Emelie Chandni Jutvik')

#######################
# SELECTED DATES
ls_dates = df_energy.groupby(['date']).count().index
selected_date = st.selectbox('Select a date', ls_dates) #date_list   
df_date = df_results[df_results.date == selected_date]
df_date_score = df_date[df_date.score_smooth >= 8]
list_of_peaks = calendar_popdown(df_date_score)
#selected_weekday = df_date['weekday_text'].iloc[0]

# ENERGY
df_energy_date = df_energy[df_energy['date'] == selected_date]
df_energy_plot = energy_differ(df_energy_date)
print(df_energy_date)

# ACTIVITY
df_activity = df_energy_date[df_energy_date['section'] != 'REST']

# SPORT
df_sports_date = df_sports[df_sports['Date'] == selected_date]

# SLEEP
df_sleep_date = df_sleep[df_sleep['date'] == selected_date]

# CALENDAR   
df_calendar_date = calendar_selection(df_calendar, selected_date)

# NOTES  
df_note_date = note_selection(df_notes, selected_date)
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
    
    st.markdown('#### Events') 
    st.caption("_:blue[Calendar notes]_ from selected day")
    st.dataframe(df_calendar_date,
                 column_order=("date", "time", "event"),
                 hide_index=True,
                 width=600,
                 column_config={
                    "date": st.column_config.TextColumn(
                        "Date",
                    ),
                    "time": st.column_config.TextColumn(
                        "Time",
                    ),
                    "event": st.column_config.TextColumn(
                        "Description",
                    )}
                 )
    
    st.caption("_:blue[Your own diary notes]_ from selected day")
    st.dataframe(df_note_date,
                 column_order=("date", "time", "note"),
                 hide_index=True,
                 width=600,
                 column_config={
                    "date": st.column_config.TextColumn(
                        "Date",
                    ),
                    "time": st.column_config.TextColumn(
                        "Time",
                    ),
                    "note": st.column_config.TextColumn(
                        "Description",
                    )}
                 )

    st.markdown('#### Diary') 
    st.caption("Make _:blue[your own notes]_ refering to detected stress peaks")
    selected_peak = st.selectbox('Select a peak', list_of_peaks)   
    options = st.multiselect(
        "Did you experience any of the following physical expressions at _:blue[selected stress peak]_?",
        ["Anxiety", "Panik attack", "Neausa", "Palpitation", "Tense", "None"],
    )  
    st.text_input('Create a note:', key='widget', on_change=clear_text)
    my_text = st.session_state.get('my_text', '') 
        


    