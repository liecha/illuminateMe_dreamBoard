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
df_results = pd.read_csv('data/ai-model/ai-model-results.csv')
df_sports = pd.read_csv('data/wearable/sports-results.csv')
df_sleep = pd.read_csv('data/wearable/sleep-results.csv')
df_calendar = pd.read_csv('data/calendar/calendar-results.csv')
df_notes = pd.read_csv('data/notes/note-results.csv')
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
    result_score_10 = df_results[df_results['Stress score'] >= 8]
    date_list_score = result_score_10.groupby(['date']).count()    
    date_list_score['date'] = date_list_score.index
    date_text = date_to_text(result_score_10, date_list_score['date'].values)
    date_list_score.insert(0, 'Day/Month/Weekday', date_text)
    date_list_score = date_list_score[['date', 'Day/Month/Weekday', 'Stress score']]
    date_list_score.rename(columns={"Stress score": "Counted stress peaks"}, inplace = True)
    date_list_score = date_list_score.sort_values(by=['Day/Month/Weekday'])
    return date_list_score

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
# Sidebar
with st.sidebar:
    st.image("illuminateMe_logo.png")  
    
    # SCORE OVERVIEW
    
    # SCORE SELECTION
    # Stress scale:
    # 1: diff == 0-5
    # 2: diff == 5-10
    # 4: diff == 10-20
    # 6: diff == 20-30
    # 8: diff == 30-40
    # 10: diff == 40-   
    stress_scores = [10, 8, 6, 4, 2, 1]
    all_weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    selected_score = st.selectbox('Select score', stress_scores)
    df_score = df_results[df_results['Stress score'] >= selected_score]
    df_period_peak_summary = weekday_summary_peaks(df_results)
    print(df_period_peak_summary)
       
    # DATE SELECTION
    date_list_score = df_score.groupby(['date']).count()
    date_list = date_list_score.index
  
    # SELECTED DATES
    selected_date = st.selectbox('Select a date', date_list)
    df_date_score = df_score[df_score.date == selected_date]
    list_of_peaks = calendar_popdown(df_date_score)
        
    df_date = df_results[df_results.date == selected_date]
    selected_weekday = df_date['weekday_text'].iloc[0]

    # SPORT
    df_sports_date = df_sports[df_sports['Date'] == selected_date]

    # SLEEP
    df_sleep_date = df_sleep[df_sleep['date'] == selected_date]
    
    # CALENDAR   
    df_calendar_date = calendar_selection(df_calendar, selected_date)
    
    # NOTES  
    df_note_date = note_selection(df_notes, selected_date)


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
st.caption("_Client_")
st.subheader('Anna Andersson')
col = st.columns((3.0, 5.5), gap='medium')

with col[0]:
    st.markdown('#### Stress peaks')
    st.caption("The selected day is a _:blue[" + selected_weekday + "]_")
    st.dataframe(df_date_score,
                 column_order=("date", "time", "Stress score"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "date": st.column_config.TextColumn(
                        "Date",
                    ),
                    "time": st.column_config.TextColumn(
                        "Time",
                    ),
                    "score": st.column_config.ProgressColumn(
                        "Score",
                        format="%f",
                        min_value=0,
                        max_value=max(df_date_score['Stress score']),
                     )}
                 )

    st.markdown('#### Period summary')  
    st.caption("Detected _:blue[stress peaks]_ for this period")
    summary_peaks_score_plot = make_barplot(df_period_peak_summary, 'date', 'Counted stress peaks')
    st.altair_chart(summary_peaks_score_plot, use_container_width=True)
    
    st.markdown('#### Sleep')
    st.caption("You where sleeping for _:blue[" + df_sleep_date['totalSleep_hours'].values[0] + "]_  at selected date")
    categories_sleep = ['deep sleep', 'shallow sleep', 'awake']
    values = df_sleep_date[['DeepSleep %', 'ShallowSleep %', 'Awake %']].values[0]
    source = pd.DataFrame({
        "category": categories_sleep,
        "value": values
    })
    donut_sleep = make_donut(source)
    st.altair_chart(donut_sleep, use_container_width=True)
    
    with st.expander('About deep sleep', expanded=True):
        st.caption('''
            Deep sleep typically happen during the first half of the night. 
            It is recommended to aim for about _:blue[13 to 23 percent]_ of your sleep 
            to be in this stages. This means - if you sleep 8 hours, you should 
            aim to get between an hour or just under two hours of deep sleep.
            ''')
    
with col[1]:          
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
    # https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
    st.markdown('#### Diary') 
    st.caption("Make _:blue[your own notes]_ refering to detected stress peaks")
    selected_peak = st.selectbox('Select a peak', list_of_peaks)   
    options = st.multiselect(
        "Did you experience any of the following physical expressions at _:blue[selected stress peak]_?",
        ["Anxiety", "Panik attack", "Neausa", "Palpitation", "Tense", "None"],
    )  
    st.text_input('Create a note:', key='widget', on_change=clear_text)
    my_text = st.session_state.get('my_text', '')
    
    st.markdown('#### Activity')  
    st.caption("_:blue[Wearable activities]_ from selected day")
    barplot_sport = make_barplot(df_sports_date, 'Time / Activity', 'Activity (minutes)')
    st.altair_chart(barplot_sport, use_container_width=True)
    
    st.markdown('#### Day overview') 
    st.caption("All _:blue[stress scores]_ at selected day")
    lineplot_score = make_lineplot(df_date, 'Stress score', 'time')
    st.altair_chart(lineplot_score, use_container_width=True)
    