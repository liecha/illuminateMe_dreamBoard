import pandas as pd
import datetime

# Functions
def pick_date(x):
    this_date = x.date()
    return this_date

def pick_time(x):
    this_time = x.time().strftime("%H:%M")
    return this_time

def date_time_insert(dataframe, format):
    date_time = pd.to_datetime(dataframe['start'], format=format)
    dataframe.insert(0, 'date_time', date_time)
    date = dataframe['date_time'].apply(pick_date)
    dataframe.insert(1, 'date', date)
    time = dataframe['date_time'].apply(pick_time)
    dataframe.insert(2, 'time', time)
    dataframe = dataframe.drop(['date_time', 'start', 'end', 'unknown_1'], axis=1)
    return dataframe

def food_sectioning(df_food):
    temp_storage_food = []
    for i in range(0, len(df_food)):
        string_array = df_food['label'].iloc[i].split('/')
        data = {
            'date': df_food['date'].iloc[i],
            'time': df_food['time'].iloc[i],
            'section': string_array[0],
            'calorie': int(string_array[1]),
            'protein': int(string_array[2]),
            'note': df_food['note'].iloc[i],
        }
        temp_storage_food.append(data)
    df_temp_food = pd.DataFrame(temp_storage_food)
    return df_temp_food

def walk_sectioning(df_walk):
    temp_storage_walk = []
    for i in range(0, len(df_walk)):
        string_array = df_walk['label'].iloc[i].split('/')
        data = {
            'date': df_walk['date'].iloc[i],
            'time': df_walk['time'].iloc[i],
            'section': string_array[0],
            'distance': string_array[1],
            'calorie': -1 * int(string_array[2]),
            'note': df_walk['note'].iloc[i],
        }
        temp_storage_walk.append(data)
    df_temp_walk = pd.DataFrame(temp_storage_walk)
    return df_temp_walk

def training_sectioning(df_training):
    temp_storage_training = []
    for i in range(0, len(df_training)):
        string_array = df_training['label'].iloc[i].split('/')
        data = {
            'date': df_training['date'].iloc[i],
            'time': df_training['time'].iloc[i],
            'section': string_array[0],
            'type': string_array[1],
            'calorie': -1 * int(string_array[2]),
            'note': df_training['note'].iloc[i],
        }
        temp_storage_training.append(data)
    df_temp_training = pd.DataFrame(temp_storage_training)
    return df_temp_training



def data_processing():
    
    # Definig constats
    now = datetime.datetime.utcnow().date()
    weight = 50
    height = 170
    age = 42
    BMR = int(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))

    # Read data
    df_food_irl = pd.read_csv('data/irl_calendars/food_irl.csv').sort_values(['start'])
    df_walk_irl = pd.read_csv('data/irl_calendars/walk_irl.csv').sort_values(['start'])
    df_training_irl = pd.read_csv('data/irl_calendars/training_irl.csv').sort_values(['start'])
    df_energy = pd.read_csv('data/irl_calendars/energy_template.csv')
    
    # Prepare datasets
    df_food_irl = date_time_insert(df_food_irl, "%Y-%m-%dT%H:%M:%S+01:00")
    df_food_irl = df_food_irl[df_food_irl['date'] <= now]
    df_temp_food_irl = food_sectioning(df_food_irl)
    
    df_walk_irl = date_time_insert(df_walk_irl, "%Y-%m-%dT%H:%M:%S+01:00")
    df_walk_irl = df_walk_irl[df_walk_irl['date'] <= now]
    df_temp_walk_irl = walk_sectioning(df_walk_irl)
    
    df_training_irl = date_time_insert(df_training_irl, "%Y-%m-%dT%H:%M:%S+01:00")
    df_training_irl = df_training_irl[df_training_irl['date'] <= now]
    df_temp_training_irl = training_sectioning(df_training_irl)
    
    df_energy['section'] = 'REST'
    df_energy['calorie'] = -1 * (BMR / 24)
    
    ls_dates = df_food_irl.groupby(['date']).count().index
    temp_store_energy = []
    for i in range(0, len(ls_dates)):
        df_food_day = df_temp_food_irl[df_temp_food_irl['date'] == ls_dates[i]]
        df_walk_day = df_temp_walk_irl[df_temp_walk_irl['date'] == ls_dates[i]]
        df_training_day = df_temp_training_irl[df_temp_training_irl['date'] == ls_dates[i]]
        df_energy['date'] = ls_dates[i]
        df_energy_day = pd.concat([df_energy, df_food_day, df_walk_day, df_training_day]).sort_values(['time'])
        temp_store_energy.append(df_energy_day)
    
    df_energy_result = pd.concat(temp_store_energy)
    df_energy_result = df_energy_result[['date', 'time', 'section', 'calorie', 'protein', 'distance', 'type', 'note']]
    df_energy_result = df_energy_result.fillna(0).sort_values(['date', 'time'])
    
    ls_dates = df_energy_result.groupby(['date']).count().index
    
    storage = []
    for j in range(0, len(ls_dates)):
        df_day = df_energy_result[df_energy_result['date'] == ls_dates[j]]
        ls_calories = df_day['calorie'].values
        ls_protein = df_day['protein'].values
        ls_acc_calories = [ls_calories[0]]
        ls_acc_protein = [ls_protein[0]]
        for i in range(0, len(ls_calories) - 1):
            counting_calories = ls_acc_calories[i] + ls_calories[i + 1]
            counting_protein = ls_acc_protein[i] + ls_protein[i + 1]
            ls_acc_calories.append(counting_calories) 
            ls_acc_protein.append(counting_protein)
        df_day.insert(3, 'calorie_acc', ls_acc_calories)
        df_day.insert(5, 'protein_acc', ls_acc_protein)
        storage.append(df_day)
    
    df_energy_acc = pd.concat(storage)
    new_column_acc = []
    for i in range(0, len(df_energy_acc)):  
        if df_energy_acc['protein'].iloc[i] == 0.0: #df_energy_acc['protein']
            new_column_acc.append(df_energy_acc['protein'].iloc[i])
        else:
            new_column_acc.append(df_energy_acc['protein_acc'].iloc[i+1])
    df_energy_acc.insert(6, 'pro_acc_clean', new_column_acc)
        
    df_energy_acc.to_csv('data/energy-irl-results.csv', index=False)