#!/usr/bin/env python3
from typing import OrderedDict
import json
import base64
import sys
from pathlib import Path
from helpers import map_boat, topLevelFields, dump

def get_boat(data, pickers):
  boat = OrderedDict()
  for field in topLevelFields:
    if field in data and data[field] is not None:
      f = data[field]
      if field in ['design_class']:
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

def merge_field(field, keep, merge):
  for val in merge:
    print(f'replace {val} with {keep} as {field} for all boats')

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
  for field in data.keys():
    rec = data[field]
    merge_field(field, rec['keep'], rec['merge'])