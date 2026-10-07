#!/usr/bin/env python3
import yaml
import json
from os import listdir
from os.path import isfile, join

def picklists():
  mypath='picklists'
  onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
  data = {}
  for f in onlyfiles:
    with open(f"picklists/{f}", "r") as stream:
      try:
        l = yaml.safe_load(stream)
        field = f.replace('.yaml', '')
        data[field] = l
      except yaml.YAMLError as exc:
        print(exc)
  return data

def boatnames():
  mypath='boat'
  boats = listdir(mypath)
  names = set()
  for b in boats:
    try:
      with open(f"boat/{b}/boat.yml", "r", encoding='utf-8') as stream:
        boat = yaml.safe_load(stream)
    except:
      print(f'boat with OGA number {b} has invalid YAML.')
    if boat['name'] is not None:
      names.add(boat['name'])
    if 'previous_names' in boat and boat['previous_names'] is not None:
      try:
        names.update(set(boat['previous_names']))
      except:
        print(f'boat with OGA number {b} has invalid previous names.')
  names.remove(None)
  names.remove('')
  return sorted(names, key=lambda n: n.upper())

data = picklists()
data['boat'] = boatnames()
with open('pickers.json', 'w') as f:
  json.dump(data, f, ensure_ascii=False)
for key in data.keys():
  with open(f'{key}.json', 'w') as f:
    json.dump(data[key], f, ensure_ascii=False)
