#!/usr/bin/env python3
import json
from os import listdir
from make_filterable import get_boat, json_serial

if __name__ == '__main__':
  mypath = 'boat'
  boats = listdir(mypath)
  data = set()
  for b in boats:
    boat = get_boat(f"{mypath}/{b}/boat.yml")
    if boat and 'place_built' in boat:
      data.add(boat['place_built'])
  with open("places.json", "w") as stream:
      json.dump(sorted(list(data)), stream, ensure_ascii=False, default=json_serial)
