import yaml
import json
from os import listdir
from os.path import isfile, join
from pathlib import Path

def ownerSortOrder(o):
  if 'start' in o:
    try:
      return int(o['start'])
    except:
      pass
  return 1800

def map_boat(item):
  boat = {k: v for k, v in item.items() if v is not None}
  if 'ownerships' in boat:
    os = boat['ownerships']
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
            ol.append(o)
      boat['ownerships'] = ol
    else:
      boat['ownerships'] = owners
  boat.pop('genericTypeByGenericType', None)
  boat.pop('rigTypeByRigType', None)
  if 'constructionMaterialByConstructionMaterial' in boat:
    boat['construction_material'] = boat['constructionMaterialByConstructionMaterial']['name']
    del boat['constructionMaterialByConstructionMaterial']
  if 'constructionMethodByConstructionMethod' in boat:
    boat['construction_method'] = boat['constructionMethodByConstructionMethod']['name']
    del boat['constructionMethodByConstructionMethod']
  if 'designer' in boat:
    boat['designer'] = { 'name': boat['designerByDesigner']['name'], 'id': boat['designer'] }
    del boat['designerByDesigner']
  if 'builder' in boat:
    boat['builder'] = { 'name': boat['builderByBuilder']['name'], 'id': boat['builder'] }
    del boat['builderByBuilder']
  return boat

mypath='page-data/boat'
boats = listdir(mypath)
data = {}
for b in boats:
  with open(f"{mypath}/{b}/page-data.json", "r") as stream:
    try: 
      data = json.load(stream)
      boat = data['result']['pageContext']['boat']
    except Exception as e:
      print(e)
      print('OGA', b)
    if boat is None:
      print(b)
    else:
      outdir = f"boat/{b}"
      Path(outdir).mkdir(parents=True, exist_ok=True)
      with open(f'{outdir}/boat.yml', 'w') as outfile:
        yaml.dump(map_boat(boat), outfile, default_flow_style=False)

