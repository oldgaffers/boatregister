#!/usr/bin/env python3
from typing import OrderedDict
import json
import yaml
import base64
import sys
from os import listdir
from pathlib import Path
from helpers import dump

def replace(field, merge, new):
  if isinstance(field, list):
    l = field
  else:
    l = [field]
  print('F', l, merge, new)
  without = [f for f in l if f['name'] not in merge]
  if len(without) == len(field):
    return field # old not present
  without.append(new)
  return without

def merge_boats(field, merge, new):
  boats = listdir('boat') # ?
  for b in boats:
    boat = None
    p = f"boat/{b}/boat.yml"
    with open(p, "r", encoding='utf-8') as stream:
      boat = yaml.safe_load(stream)
    boat[field] = replace(boat.get(field, []), merge, new)
    with open(p, 'w') as outfile:
      dump(boat, outfile)

def merge_field(field, keep, merge):
  with open("pickers.json", "r") as stream:
    pickers = json.load(stream)
  pl = pickers[field]
  new = [p for p in pl if p['name'] == keep][0]
  print(f'replace {', '.join(merge)} with {keep} as {field} for all boats')
  merge_boats(field, merge, new)
  print(f'remove {merge} from {field} picklist')
  pl2 = [p for p in pl if p['name'] not in merge]
  # save pl2 as yaml

if __name__ == '__main__':
  with open("pickers.json", "r") as stream:
    pickers = json.load(stream)
  if len(sys.argv) == 2:
    b64 = open(sys.argv[1], "r").read()
  else:
    b64 = sys.stdin.buffer.read()
  decoded = base64.b64decode(b64)
  data = json.loads(decoded)
  print(json.dumps(data))
  merge_field(data['field'], data['keep'], data['merge'])
  
