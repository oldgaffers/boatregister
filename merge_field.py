#!/usr/bin/env python3
from typing import OrderedDict
import json
import yaml
import base64
import sys
import os
from pathlib import Path
from helpers import map_boat, topLevelFields, dump

def get_boat(b):
  boat = None
  with open(f"boat/{b}/boat.yml", "r", encoding='utf-8') as stream:
    boat = yaml.safe_load(stream)
  return boat

def replace(field, old, new, pl):
  without = [f for f in field if f['name'] == 'old']
  if len(without) == len(field):
    return field # old not present
  return without + [p for p in pl if p['name'] == new]

def merge_boats(field, old, new):
  boats = listdir('boat')
  for b in boats:
    boat = get_boat(b)
    boat[field] = replace(boat[field], old, new)

def merge_field(field, keep, merge):
  for val in merge:
    print(f'replace {val} with {keep} as {field} for all boats')
    merge_boats(field, val, keep)
  print(f'TODO, remove {merge} from {field} picklist')

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