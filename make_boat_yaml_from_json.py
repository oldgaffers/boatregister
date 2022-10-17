from typing import OrderedDict
import yaml
import json
from os import listdir
from os.path import isfile, join
from pathlib import Path

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
  'builder',
  'place_built',
  'construction_material',
  'spar_material',
  'construction_method',
  'construction_details',
  'engine_installations',
  'for_sales',
  'dimensions',
  'home_country',
  'home_port',
  'hull_form',
  'reference',
  'sail_number',
  'ssr',
  'uk_part1',
  'callsign',
  'ownerships',
  'updated_at',
  'website',
  'id',
]

#   'draft',   'handicap_data',   'length_on_deck',


def ownerSortOrder(o):
  if 'start' in o:
    try:
      return int(o['start'])
    except:
      pass
  return 1800

def simplify(field, new_field, boat):
  long_field = f"{field}By{field[0].capitalize()}{field[1:]}"
  if long_field in boat:
    if field in boat:
      boat[field] = { 'name': boat[long_field]['name'], 'id': boat[field] }
    elif new_field in boat:
      boat[new_field] = { 'name': boat[long_field]['name'], 'id': boat[new_field] }
    del boat[long_field]

def ownerships(os):
  if 'owners' in os and os['owners'] is not None:
    owners = sorted(os['owners'], key=ownerSortOrder)
  else:
    owners = []
  if 'current' in os and os['current'] is not None:
    current = os['current']
    for o in current:
      ol = []
      found = False
      if 'id' in o:
        for r in owners:
          if 'id' in r and r['id'] == o['id']:
            r['current'] = True
            found = True
          ol.append(r)
        if not found:
          o['current'] = True
          if 'start' not in o:
            o['start']='?'
          ol.append(o)
      else:
        for r in owners:
          if 'member' in r and r['member'] == o['member']:
            r['current'] = True
            found = True
          ol.append(r)
        if not found:
          o['current'] = True
          if 'start' not in o:
            o['start']='?'
          print(o)
          ol.append(o)
          print(ol)
    return ol
  else:
    return owners

def map_boat(item):
  boat = {k: v for k, v in item.items() if v is not None}
  if 'ownerships' in boat:
    boat['ownerships'] = ownerships(boat['ownerships'])
  boat.pop('genericTypeByGenericType', None)
  boat.pop('rigTypeByRigType', None)
  if 'constructionMaterialByConstructionMaterial' in boat:
    boat['construction_material'] = boat['constructionMaterialByConstructionMaterial']['name']
    del boat['constructionMaterialByConstructionMaterial']
  if 'constructionMethodByConstructionMethod' in boat:
    boat['construction_method'] = boat['constructionMethodByConstructionMethod']['name']
    del boat['constructionMethodByConstructionMethod']
  simplify('designer', 'designer', boat)
  simplify('builder', 'builder', boat)
  simplify('designClass', 'design_class', boat)
  return boat

def get_boat(b):
  with open(f"{mypath}/{b}/page-data.json", "r") as stream:
    data = json.load(stream)
    data = data['result']['pageContext']['boat']
    boat = OrderedDict()
    for field in topLevelFields:
      if field in data:
        if data[field] is not None:
          boat[field] = data[field]
        del data[field]
    return boat | data # any fields not in topLevelFields

mypath='page-data/boat'
boats = listdir(mypath)
data = {}
for b in boats:
  boat = None
  try:
    boat = get_boat(b)
  except:
    print(b)
  if boat is not None:
    outdir = f"boat/{b}"
    Path(outdir).mkdir(parents=True, exist_ok=True)
    with open(f'{outdir}/boat.yml', 'w') as outfile:
      yaml.dump(map_boat(boat), outfile, default_flow_style=False, sort_keys=False)

