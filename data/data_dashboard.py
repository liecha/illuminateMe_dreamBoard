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

def text_dates(df_energy_date):
    text_date = df_energy_date['date'].iloc[0]
    current_date = datetime.strptime(text_date, "%Y-%m-%d").day
    text_month = find_month(df_energy_date)
    text_weekday = find_weekday(df_energy_date)
    return current_date, text_month, text_weekday

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
                food_string = df_activity['label'].iloc[i] + ': ' + df_activity['note'].iloc[i]
                note_storage.append(food_string)
            if labels[i] == 'TRAINING':
                if activities[i] == 'Walk':
                    walk_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(walk_string)
                if activities[i] == 'SWIM':
                    swim_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(swim_string)
                if activities[i] == 'RUN':
                    run_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(run_string)
                if activities[i] == 'BIKE':
                    bike_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['note'].iloc[i] 
                    note_storage.append(bike_string)
                if activities[i] == 'STR':
                    str_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['note'].iloc[i]
                    note_storage.append(str_string)  
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
                food_string = df_activity['label'].iloc[i] + ': ' + df_activity['note'].iloc[i]
                note_storage.append(food_string)
            if labels[i] == 'TRAINING':
                if activities[i] == 'Walk':
                    walk_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(walk_string)
                if activities[i] == 'SWIM':
                    swim_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(swim_string)
                if activities[i] == 'RUN':
                    run_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['distance'].iloc[i]
                    note_storage.append(run_string)
                if activities[i] == 'BIKE':
                    bike_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['note'].iloc[i] 
                    note_storage.append(bike_string)
                if activities[i] == 'STR':
                    str_string = df_activity['label'].iloc[i] + ': ' + activities[i] + ' ' + df_activity['note'].iloc[i]
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