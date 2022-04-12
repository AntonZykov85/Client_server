import yaml

races_dict = {'races': ['humans', 'elfs', 'dwars', 'orcs', 'ogres', 'goblins', 'hobbits'],
           'races_quantity': 7,
           'races_health': {'humans': '@1000@',
                           'elfs': '@900@',
                           'dwars': '@1200@',
                           'orcs': '@1500@',
                            'ogres': '@5000@',
                            'goblins': '@800@',
                            'hobbits': '@800@'}
           }

with open('races.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(races_dict, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open("races.yaml", 'r', encoding='utf-8') as file_new:
    new_races_dict = yaml.load(file_new, Loader=yaml.SafeLoader)

print(races_dict == new_races_dict)
