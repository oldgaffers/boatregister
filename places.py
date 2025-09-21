#!/usr/bin/env python3
import json
from os import listdir
from make_filterable import get_boat, json_serial

if __name__ == '__main__':
  mypath = 'boat'
  boats = listdir(mypath)
  data = {}
  for b in boats:
    boat = get_boat(f"{mypath}/{b}/boat.yml")
    if boat and 'place_built' in boat:
      place = boat['place_built'].strip()
      rec = data.get(place, {"place": place, "count": 0, "yards": {}})
      rec['count'] += 1
      if type(boat.get('builder')) == list:
        if len(boat['builder']) > 0:
          yard = boat['builder'][0].get('name', '').strip()
      else:
        yard = boat.get('builder', {}).get('name', '').strip()
      if yard:
        y = rec['yards'].get(yard, {"count": 0, "name": yard  })
        y['count'] += 1
        rec['yards'][yard] = y
      data[place] = rec
  with open("places.json", "w") as stream:
      json.dump(data, stream, ensure_ascii=True, default=json_serial)
  

