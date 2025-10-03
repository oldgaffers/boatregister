#!/usr/bin/env python3
import json
from os import listdir
from make_filterable import get_boat, json_serial

def get_place_data(boat, place, data):
  rec = data.get(place, {"place": place, "count": 0, "yards": {}, "no_yard": []})
  rec['count'] += 1
  yards = []
  if type(boat.get('builder')) == list:
    for b in boat['builder']:
      yards.append(b.get('name', '').strip())
  else:
    name = boat.get('builder', {}).get('name', '').strip()
    if name != '':
      yards.append(name)
  for yard in yards:
    y = rec['yards'].get(yard, {"count": 0, "name": yard  })
    y['count'] += 1
    rec['yards'][yard] = y
  if len(yards) == 0:
    rec['no_yard'].append(boat['oga_no'])
  return rec

if __name__ == '__main__':
  mypath = 'boat'
  boats = listdir(mypath)
  data = {}
  for b in boats:
    boat = get_boat(f"{mypath}/{b}/boat.yml")
    if boat and 'place_built' in boat:
      place = boat['place_built'].strip()
      data[place] = get_place_data(boat, place, data)
  with open("places.json", "w") as stream:
      json.dump(data, stream, ensure_ascii=True, default=json_serial)
  

