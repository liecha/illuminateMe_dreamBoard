from data.nutritions import locate_eatables
from data.nutritions import code_detector
from data.nutritions import def_recipie
from data.nutritions import list_all_meals
from data.nutritions import meal_search
from data.nutritions import add_meal_db
from data.nutritions import list_meal_content

name_meal = 'Mellis'
meal_dict = {
    'Ica ljust frö': 0.25,
    'Bregott': 0.05,
    'Jordnötssmör': 0.05,
    'Swebar kladdkaka': 0.06,
    'Swebar chokladboll': 0.06,
    }

#list_all_meals()
#meal_search(name_meal)
#list_meal_content(name_meal)


df_meal = locate_eatables(meal_dict)
code_meal = code_detector(meal_dict, df_meal)
def_recipie(name_meal, code_meal, meal_dict)

add_meal_db(name_meal, code_meal, meal_dict)