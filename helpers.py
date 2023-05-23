from typing import OrderedDict
import json
from markdownify import markdownify

omitFields = ['price','update_id']

topLevelFields = [
  'name',
  'oga_no',
  'generic_type',
  'rig_type',
  'mainsail_type',
  'short_description',
  'full_description',
  'year',
  'year_is_approximate',
  'designer',
  'design_class',
  'builder',
  'place_built',
  'construction_material',
  'spar_material',
  'construction_method',
  'construction_details',
  'engine_installations',
  'selling_status',
  'for_sales',
  'dimensions',
  'home_country',
  'home_port',
  'hull_form',
  'reference',
  'sail_number',
  'fishing_number',
  'mssi',
  'ssr',
  'callsign',
  'uk_part1',
  'nhsr',
  'nsbr',
  'ownerships',
  'website',
  'image_key',
  'draft',
  'handicap_data',
  'created_at',
]

def simplify(field, new_field, boat):
  long_field = f"{field}By{field[0].capitalize()}{field[1:]}"
  if long_field in boat:
    print(boat[long_field])
    if field in boat:
      boat[field] = { 'name': boat[long_field]['name'], 'id': boat[field] }
    elif new_field in boat:
      boat[new_field] = { 'name': boat[long_field]['name'], 'id': boat[new_field] }
    del boat[long_field]

def ownerSortOrder(o):
  if 'start' in o:
    try:
      return int(o['start'])
    except:
      pass
  return 1800

def owner(o):
  fields = ['name', 'member', 'id', 'start', 'end', 'share', 'current', 'note', 'text']
  r = {}
  for field in fields:
    if field in o:
      r[field] = o[field]
  return r

def ownerships(os):
  if type(os) is list:
    owners = os
  else:
    if 'owners' in os:
      nonmembers = [o for o in os['owners'] if 'member' not in o]
      members = [o for o in os['owners'] if 'member' in o]
    else:
      nonmembers = []
      members = []
    if 'current' in os:
      m = []
      for c in os['current']:
        if 'id' in c:
          n = [{**n, **c, 'current': True} for n in members if 'id' in n and n['id'] == c['id']]
        else:
          n = [{**n, **c, 'current': True} for n in members if n['member'] == c['member']]
        if (len(n) > 0):
          m.append(n[0])
      members = m
    owners = members+nonmembers
  return sorted([owner(o) for o in owners], key=ownerSortOrder)

handicapFields = [
  'thcf',
  'calculated_thcf',
  'beam',
  'draft',
  'fore_triangle_height',
  'fore_triangle_base',  
  'length_overall',
  'length_on_deck',
  'length_on_waterline',
  'length_over_spars',
  'propellor',
  'sailarea',
  'main'
  'mizzen',
  'topsail',  
]

def map_handicap_data(b):
  boat = {**b}
  if 'handicap_data' in boat:
    h = boat['handicap_data']
  else:
    h = {}
  for f in ['beam','draft','length_on_deck']:
    if f in boat:
      h[f] = boat[f]
      del boat[f]
  r = {}
  for f in handicapFields:
    if f in h:
      if h[f]:
        r[f] = h[f]
      del h[f]
  boat['handicap_data'] = {**r, **h}
  return boat

def falsy(v):
  if v is None:
    return True
  if v == '':
    return True
  if v == 'null':
    return True
  if v == 'true':
    return True
  return False

def map_for_sale(fs):
  r = {k: v for k, v in fs.items() if not falsy(v)}
  if 'sales_text' in r:
    r['sales_text'] = markdownify(r['sales_text'], wrap=True)
  return r

def map_boat(item):
  boat = {k: v for k, v in item.items() if not falsy(v) and k not in omitFields}
  if 'ownerships' in boat:
    boat['ownerships'] = ownerships(boat['ownerships'])
  if 'short_description' in boat:
    boat['short_description'] = markdownify(boat['short_description'], wrap=True)
  if 'full_description' in boat:
    boat['full_description'] = markdownify(boat['full_description'], wrap=True)
  if 'for_sales' in boat:
    boat['for_sales'] = [map_for_sale(fs) for fs in boat['for_sales']]
  if 'design_class' in boat:
    if 'examples' in boat['design_class']:
      del boat['design_class']['examples']
  return map_handicap_data(boat)

def get_boat(indata):
  boat = OrderedDict()
  data = json.loads(json.dumps(indata))
  for field in topLevelFields:
    if field in data and data[field] is not None:
      f = data[field]
      if field in ['builder','designer','design_class']:
        if type(f) is dict:
          id = f['id']
        else:
          id = f
        values = [p for p in pickers[field] if p['id'] == id]
        if (len(values) > 0):
          boat[field] = values[0]
      else:
        boat[field] = f
      del data[field]
  return OrderedDict(**boat, **OrderedDict(data)) # any fields not in topLevelFields

def merge_object(existing, changes):
  if existing is None:
    merged = OrderedDict()
  else:
    merged = OrderedDict(**existing)
  print(changes)
  for key in changes.keys():
    t = type(changes[key])
    if t == dict:
      if key in existing:
        merged[key] = merge_object(existing[key], changes[key])
      else:
        merged[key] = changes[key]
    elif t == list:
      if key in existing:
        a = [json.dumps(dict(sorted(v.items()))) for v in merged[key] + changes[key]]
        merged[key] = [json.loads(c) for c in list(dict.fromkeys(a))]
      else:
        merged[key] = changes[key]
    else:
      merged[key] = changes[key]
  return merged
