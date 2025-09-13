import sys
from os import listdir
import yaml
import json
from helpers import process_html, json_serialise
import thcf
from format import boatm2f

def fromYaml(b):
  boat = None
  try:
    with open(f"boat/{b}/boat.yml", "r", encoding='utf-8') as stream:
      boat = yaml.safe_load(stream)
  except:
    print(f'boat with OGA number {b} has invalid YAML.')
  if boat is not None:
    return boatm2f(process_html(boat))
  return None

def checked(hd):
  b = hd.get('checked', None)
  if b is None:
    return 'No'
  if b:
    return 'Yes'
  return 'No'

def summarise(b):
  boat = fromYaml(b)
  if boat is None:
    return None
  if 'handicap_data' not in boat or 'rig_type' not in boat:
    return [boat['name'], boat['oga_no']]
  hc = thcf.fThcf(boat)
  hd = boat['handicap_data']
  return [boat['name'], boat['oga_no'], boat.get('mainsail_type', ''), boat.get('rig_type', '').lower(), round(hc, 3), round(hd.get('thcf', 0), 3), checked(hd), hd.get('last_modified', '')]

if __name__ == '__main__':
  r = []
  if len(sys.argv) == 2:
    b = summarise(sys.argv[1])
    if b is not None:
      r.append(b)
  else:
    boats = listdir('boat')
    for boat in boats:
      b = summarise(boat)
      if b is not None:
        r.append(b)
  sep = '\t'
  print(sep.join(['Name', 'OGA No', 'Mainsail Type', 'Rig Type', 'Calculated THCF', 'Recorded THCF', 'Checked', 'Last Modified']))
  for boat in r:
    print(sep.join([f"{f}" for f in boat]))