import pandas as pd

'''
Example:
    
meal_dict = {
    'Havregryn fullkorn': 0.4,
    'Jordnötter rostade saltade': 0.1,
    'Pumpafrö': 0.1,
    'Jordnötssmör': 0.1,
    'Estrella nötmix': 0.1,
    'Protinella': 0.1,
    'Sojayoghurt': 1,
    }

'''

def locate_eatables(meal_dict):
    eatables = list(meal_dict.keys())
    found_eatables = []
    for j in range(0, len(eatables)):
        df_db = pd.read_csv('data/livsmedelsdatabas.csv')
        this_eatable = eatables[j]
        look_for_eatable = df_db.loc[df_db['livsmedel'] == this_eatable]  
       
        if len(look_for_eatable) == 0:            
            # 1 Look if eatable has other names/alternatives in the database
            contains_eatable = df_db['livsmedel'].str.contains(this_eatable).values
            df_db.insert(0, 'contains', contains_eatable)
            result_list = df_db.loc[df_db['contains'] == True]
            suggestions = result_list['livsmedel'].values
            if len(suggestions) != 0:
                print('Altenativ för ' + this_eatable + ':')
                for i in range(0, len(suggestions)):        
                    print(suggestions[i])
                print('Jag vill pausa loppen för att ge användaren alternativ på livsmedelslista som hittats.')
                break   
            else:
                print(eatables[j] + ' behöver adderas till databasen.')
                break
        else:
            found_eatables.append(look_for_eatable)
    if len(eatables) == len(found_eatables):
        df_result = pd.concat(found_eatables)
        print('Livsmedel som hittats i databasen:')
        print(df_result)
        return df_result

def code_detector(meal_dict, df_meal):
    key_list = list(meal_dict.keys())
    values_list = list(meal_dict.values())
    calories = 0.0
    protein = 0.0
    carb = 0.0
    fat = 0.0
    for i in range(0, len(key_list)):
        this_eatable = df_meal.loc[df_meal['livsmedel'] == key_list[i]]  
        calories = int(calories + this_eatable['calorie'].iloc[0] * values_list[i])
        protein = int(protein +  this_eatable['protein'].iloc[0] * values_list[i])
        carb = int(carb +  this_eatable['carb'].iloc[0] * values_list[i])
        fat = int(fat +  this_eatable['fat'].iloc[0] * values_list[i])
    food_code = 'FOOD/' + str(calories) + '/' + str(protein) + '/' + str(carb) + '/' + str(fat)
    print('Detta är din genererade kod:')
    print(food_code)
    return food_code

def def_recipie(name_meal, code_meal, meal_dict):
    meal_for_storage = {
        'name': [name_meal] * len(list(meal_dict.keys())),
        'livsmedel': list(meal_dict.keys()),
        'amount': list(meal_dict.values()),
        'code' : [code_meal] * len(list(meal_dict.keys()))
    }
    new_recipie = pd.DataFrame(meal_for_storage)
    print('Detta är dina inputs för denna måltid:')
    print(new_recipie)
    return new_recipie

def list_all_meals():
    summary = pd.read_csv('data/meal_databas.csv').groupby(['name', 'code']).count()
    print('Måltider registrerade i databasen: ')
    print()
    for i in range(0, len(summary)):       
        print(summary.index[i][0] + ' (' + summary.index[i][1] + ')' )
        
def meal_search(name_meal):
    df_meals = pd.read_csv('data/meal_databas.csv')
    look_for_recipie = df_meals.loc[df_meals['name'] == name_meal] 
    if len(look_for_recipie) == 0:
        print(name_meal + ' finns inte registrerad i databasen.')
        print()
        list_all_meals()
    else:
        df_content = look_for_recipie[['livsmedel', 'amount']]
        print('Måltid: ' + look_for_recipie['name'].iloc[0])
        print('Kod: ' + look_for_recipie['code'].iloc[0])
        print('Inndehåll:')
        print(df_content)
 
    
def add_meal_db(name_meal, code_meal, meal_dict):
    new_recipie = def_recipie(name_meal, code_meal, meal_dict)
    df_meals = pd.read_csv('data/meal_databas.csv')
    look_for_recipie = df_meals.loc[df_meals['name'] == name_meal]
    if len(look_for_recipie) != 0:
        print('Denna måltid finns redan i databasen:')
        print(look_for_recipie)
    else:
        df_add_meal = pd.concat([df_meals, new_recipie])
        df_add_meal.to_csv('data/meal_databas.csv', index=False)
        df_meals = pd.read_csv('data/meal_databas.csv')
        print(df_meals)


def list_meal_content(name_meal):
    df_meals = pd.read_csv('data/meal_databas.csv')
    look_for_meal = df_meals.loc[df_meals['name'] == name_meal]
    if len(look_for_meal) == 0:
        print(name_meal + ' finns inte registrerad i databasen.')
    else:
        df_content = look_for_meal[['livsmedel', 'amount']]
        print('Måltid: ' + look_for_meal['name'].iloc[0])
        print('Kod: ' + look_for_meal['code'].iloc[0])
        print('Inndehåll:')
        print(df_content)




