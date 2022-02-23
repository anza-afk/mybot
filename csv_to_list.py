import csv


def get_city_list(csv_file):
    """Returns a city list from provided csv."""
    cities_list = set()
    with open(csv_file, 'r', encoding='cp1251') as cty:
        fields = ['city_id', 'country_id', 'region_id', 'name']
        reader = csv.DictReader(cty, fields, delimiter=';')
        next(reader)
        for row in reader:
            cities_list.add(row['name'].lower())
    return cities_list


def get_random_city(cities_list: set, last_letter: str) -> str:
    """Returns random city with given first letter."""
    bot_word = '0'
    city_iter = iter(cities_list)
    while bot_word[0] != last_letter:
        bot_word = next(city_iter)
    return bot_word
