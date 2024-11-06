# -*- coding: utf-8 -*-

with col[2]:
    st.markdown('#### Gains/Losses')

    df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year)

    if selected_year > 2010:
        first_state_name = df_population_difference_sorted.states.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[0])
    else:
        first_state_name = '-'
        first_state_population = '-'
        first_state_delta = ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > 2010:
        last_state_name = df_population_difference_sorted.states.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.population.iloc[-1])   
        last_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[-1])   
    else:
        last_state_name = '-'
        last_state_population = '-'
        last_state_delta = ''
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

    
    st.markdown('#### States Migration')

    if selected_year > 2010:
        # Filter states with population difference > 50000
        # df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference_absolute > 50000]
        df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference > 50000]
        df_less_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference < -50000]
        
        # % of States with population difference > 50000
        states_migration_greater = round((len(df_greater_50000)/df_population_difference_sorted.states.nunique())*100)
        states_migration_less = round((len(df_less_50000)/df_population_difference_sorted.states.nunique())*100)
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')
    else:
        states_migration_greater = 0
        states_migration_less = 0
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater)
        st.write('Outbound')
        st.altair_chart(donut_chart_less)
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
            - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year
            - :orange[**States Migration**]: percentage of states with annual inbound/ outbound migration > 50,000
            ''')
            
    st.markdown('#### Weekday summary') 
    st.caption("Summary of _:blue[stress scores]_ for _:blue[" + selected_weekday + "s]_")
    lineplot_weekday_avg = make_lineplot(df_weekday_average, 'score', 'time_string')
    st.altair_chart(lineplot_weekday_avg, use_container_width=True)
    
    
    
    
        '''    
        note = st.text_input("Make a note", "I think this peak refers to...") 
        button_check = st.form_submit_button("Save")
        if button_check == True:
            st.write("Your note was saved")
            date_peak_string = selected_peak[0:10]
            time_peak_string = selected_peak[14:]
            note_dict = {
                'date': [date_peak_string],
                'time': [time_peak_string],
                'note': [note]
                }
            df_note = pd.DataFrame(note_dict) 
            df_note.to_csv('data/notes/note-results.csv', index=False)
         '''  
 def save_notes(state_variable):
     '''
     date_peak_string = selected_peak[0:10]
     time_peak_string = selected_peak[14:]
     note_dict = {
         'date': [date_peak_string],
         'time': [time_peak_string],
         'note': [note]
         }
     df_note = pd.DataFrame(data) '
     '''   
     note = {
         'date': ['date_peak_string'],
         'time': ['time_peak_string'],
         'note': [state_variable]
         }
     df_note = pd.DataFrame(note) 
     df_note.to_csv('data/notes/note-results.csv', index=False)
     print('Runned saving function...')
        
    st.markdown('#### Diary') 
    st.caption("Make _:blue[your own notes]_ refering to detected stress peaks")
     
    with st.form("key1"):
        selected_peak = st.selectbox('Select a peak', list_of_peaks)
        placeholder = st.empty()
        input_test = placeholder.text_input('Make your note')
        button_check = st.form_submit_button("Save")
        if button_check:
            input_test = placeholder.text_input('Make your note', value='', key=1)
            st.caption("_Your note was saved_") 
    
    st.title('Counter example')
    if 'count' not in st.session_state:
        st.session_state.count = 0
    
    increment = st.button('Increment')
    if increment:
        st.session_state.count += 1
        local_state_variable.append(st.session_state.count)
        save_notes(local_state_variable)
    
    with open('counter_file.pkl', 'wb') as f:  # open a text file
        pickle.dump(local_state_variable, f)
    
    st.write('Count = ', local_state_variable)
    
    
    with st.form("key=1"):
        selected_peak = st.selectbox('Select a peak', list_of_peaks)
        placeholder = st.empty()
        input_test = placeholder.text_input('Make your note')
        button_check = st.form_submit_button("Save")
        if input_test:
            input_test = placeholder.text_input('Make your note', value='', key=1)
