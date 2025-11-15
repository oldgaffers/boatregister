#!/usr/bin/env python3
import re
import yaml
import json
from os import listdir
from datetime import date, datetime

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
    'mainsail_type',
    'generic_type',
    'design_class',
    'construction_material',
    'year',
    'length_on_deck',
    'price',
    'sale',
    'sail',
    'home_port',
    'place_built',
    ]
    if 'selling_status' in boat and boat['selling_status'] == 'for_sale':
      for_sales = boat.get('for_sales', [{'asking_price': 0}])
      boat['price'] = for_sales[0].get('asking_price', 0)
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
  data = get_json('fleets/editors choice')
  editors_choice = {o:i for i,o in enumerate(data['filters']['oga_nos'])}
  last_modified = get_json('lmd.json')
  mypath='boat'
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
      boat['updated_at'] = lmd(oga_no, last_modified)
      data.append(boat)
  with open("filterable.json", "w") as stream:
      json.dump(data, stream, ensure_ascii=False, default=json_serial)
