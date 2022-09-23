import re
import yaml
import json
from os import listdir

def transform(o):
  if type(o) is dict and 'name' in o:
    return o['name']
  if type(o) is str:
    m = re.match(r'(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}.*', o)
    if m is not None:
      return m.groups()[0]
  return o

def wanted(boat):
    wanted_keys = [
    'name',
    'oga_no',
    'designer',
    'builder',
    'rig_type',
    'mainsail_type',
    'generic_type',
    'design_class',
    'construction_method',
    'year',
    'updated_at',
    'length_on_deck',
    'price',
    ]
    return { key: transform(boat[key]) for key in wanted_keys if key in boat }

mypath='boat/'
boats = listdir(mypath)
data = []
for b in boats:
  with open(f"{mypath}/{b}/boat.yml", "r") as stream:
    try: 
      boat = yaml.safe_load(stream)
      if boat is None:
        print(f'no data for {b}')
      else:
        boat = wanted(boat)
        data.append(boat)
    except Exception as e:
      print(e)
      print('OGA', b)
with open("filterable.json", "w") as stream:
    json.dump(data, stream, ensure_ascii=False)
