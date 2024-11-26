import pandas as pd
from datetime import datetime, date
import altair as alt

def date_time_now():
    date_now = date.today()
    time_now = datetime.now().time() 
    return date_now, time_now

def datetime_to_string(this_date, this_time):
    date_str = this_date.strftime("%Y-%m-%d")
    time_str = this_time.strftime("%H:%M")
    return date_str, time_str

def find_month(this_month):
    text_month = ''
    if this_month == 1:
        text_month = 'January'
    if this_month == 2:
        text_month = 'February'
    if this_month == 3:
        text_month = 'Mars'
    if this_month == 4:
        text_month = 'April'
    if this_month == 5:
        text_month = 'May'
    if this_month == 6:
        text_month = 'June'
    if this_month == 7:
        text_month = 'July'
    if this_month == 8:
        text_month = 'August'
    if this_month == 9:
        text_month = 'September'
    if this_month == 10:
        text_month = 'October'
    if this_month == 11:
        text_month = 'November'
    if this_month == 12:
        text_month = 'December'
    return text_month

def find_weekday(this_day):
    text_day = ''
    if this_day == 0:
        text_day = 'Monday'
    if this_day == 1:
        text_day = 'Thursday'
    if this_day == 2:
        text_day = 'Wednesday'
    if this_day == 3:
        text_day = 'Turesday'
    if this_day == 4:
        text_day = 'Friday'
    if this_day == 5:
        text_day = 'Saturday'
    if this_day == 6:
        text_day = 'Sunday'
    return text_day

def text_dates(selected_date):
    current_date = datetime.strptime(selected_date, "%Y-%m-%d")    
    current_day = current_date.day
    text_month = find_month(current_date.month)    
    text_weekday = find_weekday(current_date.weekday())
    return current_day, text_month, text_weekday

### ENERGY
def energy_differ(df_energy_date):
    data_e = {
        'energy': df_energy_date['energy'].values,
        'time':df_energy_date['time'].values,
        'label': ['in_out'] * len(df_energy_date)
        }
    df_e = pd.DataFrame(data_e)
    data_acc = {
        'energy': df_energy_date['energy_acc'].values,
        'time':df_energy_date['time'].values,
        'label': ['energy_acc'] * len(df_energy_date)
        }
    df_acc = pd.DataFrame(data_acc)
    df_energy_date_final = pd.concat([df_e, df_acc])
    return df_energy_date_final

def energy_at_time(df_energy_date):    
    now = datetime.now() # current date and time
    current_date = now.strftime("%Y-%m-%d")
    if df_energy_date['date'].iloc[0] < current_date:
        df_in = df_energy_date[df_energy_date['label'] == 'FOOD']
        df_out = df_energy_date[df_energy_date['label'] != 'FOOD']
        energy_in = int(sum(df_in['energy'].values))
        energy_out = int(sum(df_out['energy'].values))
        energy_balance = int(df_energy_date['energy_acc'].values[-1])    
    if df_energy_date['date'].iloc[0] == current_date:
        time = now.strftime("%H:%M:%S")
        df_energy_date_balance = df_energy_date[df_energy_date['time'] <= time]
        df_in = df_energy_date_balance[df_energy_date_balance['label'] == 'FOOD']
        df_out = df_energy_date_balance[df_energy_date_balance['label'] != 'FOOD']
        energy_in = int(sum(df_in['energy'].values))
        energy_out = int(sum(df_out['energy'].values))
        energy_balance = int(df_energy_date_balance['energy_acc'].values[-1])
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
        df_food = df_energy_date[df_energy_date['label'] == 'FOOD']       
    else:
        time = now.strftime("%H:%M:%S")
        df_food = df_energy_date[df_energy_date['time'] <= time]
        df_food = df_energy_date[df_energy_date['label'] == 'FOOD'] 
    protein_acc = sum(df_food['pro'].to_list())
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
        'nutrient': df_energy_date['pro'].values,
        'time':df_energy_date['time'].values,
        'label': ['pro'] * len(df_energy_date)
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
    df_activity = df_activity[['date', 'time', 'label', 'activity', 'distance', 'note']]   
    now = datetime.now() # current date and time
    current_date = now.strftime("%Y-%m-%d")
    if df_activity['date'].iloc[0] < current_date:
        note_storage = []
        labels = df_activity['label'].values
        activities = df_activity['activity'].values
        for i in range(0, len(labels)):
            if labels[i] == 'FOOD':
                food_string =  '🍛 ' + df_activity['note'].iloc[i]
                note_storage.append(food_string)
            if labels[i] == 'TRAINING':
                if activities[i] == 'Walk':
                    walk_string = '🚶🏻‍♂️ '  + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(walk_string)
                if activities[i] == 'SWIM':
                    swim_string = '🏊🏼‍♀️ '   + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(swim_string)
                if activities[i] == 'RUN':
                    run_string = '🏃🏽‍♂️ ' + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(run_string)
                if activities[i] == 'BIKE':
                    bike_string = '🚵🏼 ' + activities[i] + ' ' + df_activity['note'].iloc[i] 
                    note_storage.append(bike_string)
                if activities[i] == 'STR':
                    str_string = '🏋🏻‍♂️ ' + activities[i] + ' ' + df_activity['note'].iloc[i] 
                    note_storage.append(str_string)           
        df_activity.insert(6, 'summary', note_storage)
        return df_activity
    if df_activity['date'].iloc[0] == current_date:
        time = now.strftime("%H:%M:%S")
        df_activity_irl = df_activity[df_activity['time'] <= time]
        note_storage = []
        labels = df_activity_irl['label'].values
        activities = df_activity['activity'].values
        for i in range(0, len(labels)):
            if labels[i] == 'FOOD':
                food_string = '🍛 ' + df_activity['note'].iloc[i]
                note_storage.append(food_string)
            if labels[i] == 'TRAINING':
                if activities[i] == 'Walk':
                    walk_string = '🚶🏻‍♂️ ' + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(walk_string)
                if activities[i] == 'SWIM':
                    swim_string = '🏊🏼‍♀️ '   + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(swim_string)
                if activities[i] == 'RUN':
                    run_string = '🏃🏽‍♂️ ' +  activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(run_string)
                if activities[i] == 'BIKE':
                    bike_string = '🚵🏼 ' + activities[i] + ' ' + df_activity['note'].iloc[i] 
                    note_storage.append(bike_string)
                if activities[i] == 'STR':
                    str_string = '🏋🏻‍♂️ ' + activities[i] + ' ' + df_activity['note'].iloc[i]
                    note_storage.append(str_string)  
        df_activity_irl.insert(6, 'summary', note_storage)
        return df_activity_irl
    
### CHART
def make_donut(source): 
    chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
        theta="value",
        color="category:N",
    )
    return chart