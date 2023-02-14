import re
import yaml
import json
from os import listdir
from datetime import date, datetime

def transform(o):
  if type(o) is dict and 'name' in o:
    return o['name']
  if type(o) is list:
    return [f['name'] for f in o]
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
    'construction_material',
    'year',
    'updated_at',
    'length_on_deck',
    'price',
    'sale',
    ]
    if 'selling_status' in boat and boat['selling_status'] == 'for_sale':
      boat['price'] = boat['for_sales'][0]['asking_price']
      boat['sale'] = True
    else:
      boat['sale'] = False
    b = { key: transform(boat[key]) for key in wanted_keys if key in boat }
    if 'length_on_deck' not in b:
      if 'handicap_data' in boat:
        h = boat['handicap_data']
        if 'length_on_deck' in h:
          b['length_on_deck'] = h['length_on_deck']
    return b

def owners(boat):
  if 'ownerships' in boat:
    current = [o['id'] for o in boat['ownerships'] if 'id' in o and 'current' in o and o['current']]
    if len(current) == 0:
      current = [f"M{o['member']}" for o in boat['ownerships'] if 'member' in o and 'current' in o and o['current']]
    return current
  return []

def get_boat(path):
  with open(path, "r") as stream:
    try: 
      boat = yaml.safe_load(stream)
    except Exception as e:
      print(e)
      print('OGA', path)
      boat = None
  if boat is None:
    return None
  else:
    return boat

def json_serial(obj):
  if isinstance(obj, date):
    return obj.isoformat()
  if isinstance(obj, datetime):
    return obj.isoformat(timespec='seconds')[:-6]+'Z'
  raise TypeError ("Type %s not serializable" % type(obj))

if __name__ == '__main__':
  f = open('fleets/editors choice')
  data = json.load(f)
  f.close()
  editors_choice = {o:i for i,o in enumerate(data['filters']['oga_nos'])}
  mypath='boat/'
  boats = listdir(mypath)
  data = []
  for b in boats:
    fullboat = get_boat(f"{mypath}/{b}/boat.yml")
    if fullboat is not None:
      boat = wanted(fullboat)
      oga_no = int(b)
      if oga_no in editors_choice:
        boat['rank'] = editors_choice[oga_no]
      else:
        boat['rank'] = len(boats)
      if 'ownerships' in fullboat:
        boat['owners'] = owners(fullboat)
      data.append(boat)
  with open("filterable.json", "w") as stream:
      json.dump(data, stream, ensure_ascii=False, default=json_serial)
