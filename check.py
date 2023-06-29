import re
import yaml
import json
from os import listdir
from datetime import date, datetime

def get_boat(path):
  with open(path, "r") as stream:
    try: 
      boat = yaml.safe_load(stream)
    except Exception as e:
      print(e)
      print('OGA', path)
      boat = None
  if boat is None:
    return None
  else:
    return boat

if __name__ == '__main__':
  ratio = 1.6
  mypath='boat'
  boats = listdir(mypath)
  data = []
  for b in boats:
    boat = get_boat(f"{mypath}/{b}/boat.yml")
    hd = boat.get('handicap_data')
    if hd:
      loa = hd.get('length_over_all')
      if loa:
        fore_triangle_height = hd.get('fore_triangle_height')
        if fore_triangle_height:
          if ratio*loa < fore_triangle_height:
            print('fth', boat['name'], boat['oga_no'], loa, fore_triangle_height)
        ml = hd.get('main', {}).get('luff')
        if ml and ml > ratio*loa:
            print('main luff', boat['name'], boat['oga_no'], loa, ml)
        tl = hd.get('topsail', {}).get('luff')
        if tl and tl > ratio*loa:
            print('topsail luff', boat['name'], boat['oga_no'], loa, tl)