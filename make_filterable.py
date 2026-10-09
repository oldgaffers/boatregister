#!/usr/bin/env python3
import re
import yaml
import json
from os import listdir
from datetime import date, datetime
from shuffle_editors_choice import shuffle

def fn(f):
  if f is None:
    return ''
  if type(f) is str:
    return f
  try:
    return f.get('name', '')
  except:
    print(f)
  return ''

def transform(o):
  if type(o) is dict and 'name' in o:
    return o['name']
  if type(o) is list:
    return [fn(f) for f in o]
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
    'sail_type',
    'generic_type',
    'design_class',
    'construction_material',
    'year',
    'length_on_deck',
    'price',
    'offered',
    'sale',
    'sail',
    'home_port',
    'place_built',
    'previous_names',
    ]
    sailtypes = set()
    if boat.get('mainsail_type', 'none') != 'none':
      sailtypes.add(boat['mainsail_type'])
    if boat.get('handicap_data', None) is not None:
      hd = boat['handicap_data']
      for mast in ['main', 'fore', 'mizzen']:
        if hd.get(mast, None) is not None:
            st = hd[mast].get('type', None)
            if st is not None:
              sailtypes.add(st)
    boat['sail_type'] = list(sailtypes)
    if 'selling_status' in boat and boat['selling_status'] == 'for_sale' and len(boat.get('for_sales', [])) > 0:
      for_sales = sorted(boat['for_sales'], key=lambda d: d['created_at'], reverse=True)
      fsr = for_sales[0]
      boat['price'] = fsr.get('asking_price', 0)
      boat['offered'] = fsr.get('created_at', '')[0:10]
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
  try:
    with open(path, "r", encoding='utf-8') as stream:
      return yaml.safe_load(stream)
  except Exception as e:
    print(e)
    print('OGA', path)
  return None

def json_serial(obj):
  if isinstance(obj, date):
    return obj.isoformat()
  if isinstance(obj, datetime):
    return obj.isoformat(timespec='seconds')[:-6]+'Z'
  raise TypeError ("Type %s not serializable" % type(obj))

def get_json(fn):
  a = open(fn)
  d=json.load(a)
  a.close()
  return d

def lmd(oga_no, last_modified):
  d=[r for r in last_modified if r['oga_no'] == oga_no]
  if len(d) > 0:
    if 'lmd' in d[0]:
      return d[0]['lmd'][0:10]
  return str(date.today())

if __name__ == '__main__':
  last_modified = get_json('lmd.json')
  mypath='boat'
  boats = listdir(mypath)
  editors_choice = shuffle(boats)
  data = []
  for b in boats:
    fullboat = get_boat(f"{mypath}/{b}/boat.yml")
    if fullboat is not None:
      boat = wanted(fullboat)
      oga_no = int(b)
      boat['rank'] = editors_choice.index(oga_no)
      if 'ownerships' in fullboat:
        boat['owners'] = owners(fullboat)
      boat['updated_at'] = lmd(oga_no, last_modified)
      data.append(boat)
  with open("filterable.json", "w") as stream:
      json.dump(data, stream, ensure_ascii=False, default=json_serial)
